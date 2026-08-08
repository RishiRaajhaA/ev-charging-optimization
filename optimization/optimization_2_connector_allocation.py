"""
Optimization 2 — Regional Connector Allocation

Goal:
    Given B additional EV charging connectors, allocate them across the
    administrative regions recorded in `state` so that the minimum
    connectors-per-station ratio across regions is maximized.

Why this formulation:
    We do not assume EV demand, population, traffic, revenue, or electricity
    consumption. We use only observed stations and connectors.

Decision variable:
    x_i = integer number of additional connectors allocated to region i

Auxiliary variable:
    t = minimum post-allocation connectors-per-station ratio

Objective:
    maximize t

Constraints:
    C_i + x_i >= t * S_i       for every region i
    sum_i x_i = B
    x_i >= 0 and integer
    t >= 0

This is a Mixed-Integer Linear Program (MILP): x_i are integer and t is
continuous.

Important scope:
    Only records with a non-missing `state` are included. This is explicit
    because 2,869 records in the dataset have missing state values.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix, csr_matrix


DATA_PATH = Path(__file__).parent.parent / "data" / "ev_stations_2025.csv"


def load_regional_data(data_path=DATA_PATH):
    """Load the dataset and aggregate stations/connectors by state."""
    df = pd.read_csv(data_path)

    required = {"id", "state", "num_connectors"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["num_connectors"] = pd.to_numeric(
        df["num_connectors"], errors="coerce"
    )

    regional_df = df.dropna(
        subset=["state", "num_connectors"]
    ).copy()

    regional_df = (
        regional_df.groupby("state", as_index=True)
        .agg(
            stations=("id", "size"),
            connectors=("num_connectors", "sum"),
        )
        .sort_index()
    )

    regional_df["current_cps"] = (
        regional_df["connectors"] / regional_df["stations"]
    )

    return df, regional_df


def solve_connector_allocation(regional_df, budget):
    """
    Solve the max-min regional connector allocation MILP.

    max t

    subject to:
        C_i + x_i >= t*S_i
        sum_i x_i = budget
        x_i >= 0 integer
        t >= 0
    """
    if budget < 0 or int(budget) != budget:
        raise ValueError("budget must be a non-negative integer")

    budget = int(budget)

    stations = regional_df["stations"].to_numpy(dtype=float)
    connectors = regional_df["connectors"].to_numpy(dtype=float)

    n = len(regional_df)

    # Variables:
    # x_0 ... x_(n-1), t
    t_index = n

    A = lil_matrix((n + 1, n + 1), dtype=float)
    lower = np.full(n + 1, -np.inf)
    upper = np.full(n + 1, np.inf)

    # C_i + x_i >= t*S_i
    # -x_i + S_i*t <= C_i
    for i in range(n):
        A[i, i] = -1.0
        A[i, t_index] = stations[i]
        upper[i] = connectors[i]

    # Total connector budget
    A[n, :n] = 1.0
    lower[n] = budget
    upper[n] = budget

    # Minimize -t == maximize t
    objective = np.zeros(n + 1)
    objective[t_index] = -1.0

    integrality = np.zeros(n + 1)
    integrality[:n] = 1  # x_i integer
    integrality[t_index] = 0  # t continuous

    lower_bounds = np.zeros(n + 1)
    upper_bounds = np.r_[
        np.full(n, budget, dtype=float),
        np.inf,
    ]

    result = milp(
        c=objective,
        integrality=integrality,
        bounds=Bounds(lower_bounds, upper_bounds),
        constraints=LinearConstraint(
            csr_matrix(A),
            lower,
            upper,
        ),
        options={"time_limit": 120},
    )

    if not result.success:
        raise RuntimeError(
            f"Optimization failed: {result.message}"
        )

    allocation = np.rint(result.x[:n]).astype(int)
    t = float(result.x[t_index])

    output = regional_df.copy()
    output["additional_connectors"] = allocation
    output["final_connectors"] = (
        output["connectors"] + output["additional_connectors"]
    )
    output["final_cps"] = (
        output["final_connectors"] / output["stations"]
    )

    return {
        "allocation": output,
        "minimum_cps": t,
        "budget": budget,
        "solver_result": result,
    }


def validate_solution(result):
    """Independently validate the mathematical solution."""
    allocation = result["allocation"]
    budget = result["budget"]

    checks = {}

    # Budget
    checks["budget"] = (
        int(allocation["additional_connectors"].sum()) == budget
    )

    # Non-negative integer allocation
    x = allocation["additional_connectors"]
    checks["integer_nonnegative"] = bool(
        np.all(x.to_numpy() >= 0)
        and np.all(x.to_numpy() == np.floor(x.to_numpy()))
    )

    # Independent minimum CPS
    independent_min_cps = allocation["final_cps"].min()
    solver_t = result["minimum_cps"]

    checks["objective_match"] = bool(
        np.isclose(
            independent_min_cps,
            solver_t,
            rtol=1e-8,
            atol=1e-8,
        )
    )

    # Every region must satisfy final CPS >= solver t
    checks["fairness_constraints"] = bool(
        np.all(allocation["final_cps"].to_numpy() + 1e-10 >= solver_t)
    )

    return checks, independent_min_cps


def proportional_baseline(regional_df, budget):
    """
    Baseline: allocate connectors approximately proportional to station count.
    Largest-remainder rounding ensures the exact budget is used.
    """
    stations = regional_df["stations"].to_numpy(dtype=float)
    weights = stations / stations.sum()

    raw = weights * budget
    allocation = np.floor(raw).astype(int)

    remaining = budget - allocation.sum()

    if remaining > 0:
        fractions = raw - allocation
        order = np.argsort(-fractions)
        allocation[order[:remaining]] += 1

    baseline = regional_df.copy()
    baseline["additional_connectors"] = allocation
    baseline["final_connectors"] = (
        baseline["connectors"] + baseline["additional_connectors"]
    )
    baseline["final_cps"] = (
        baseline["final_connectors"] / baseline["stations"]
    )

    return baseline


def validate_budget_sensitivity(regional_df, budgets):
    """Run the model for multiple budgets and verify min-CPS monotonicity."""
    rows = []

    for budget in budgets:
        result = solve_connector_allocation(regional_df, budget)
        checks, independent_min_cps = validate_solution(result)

        rows.append({
            "budget": budget,
            "minimum_cps": independent_min_cps,
            "total_allocated": int(
                result["allocation"]["additional_connectors"].sum()
            ),
            "all_checks_pass": all(checks.values()),
        })

    table = pd.DataFrame(rows)
    monotonic = bool(
        np.all(np.diff(table["minimum_cps"].to_numpy()) >= -1e-10)
    )

    return table, monotonic


if __name__ == "__main__":
    df, regional_df = load_regional_data()

    print("=== Optimization 2: Regional Connector Allocation ===")
    print(f"Total dataset records: {len(df):,}")
    print(f"Records with valid state: {df['state'].notna().sum():,}")
    print(f"Missing state records: {df['state'].isna().sum():,}")
    print(f"Regions included: {len(regional_df):,}")
    print(
        f"Existing connectors in modeled regions: "
        f"{regional_df['connectors'].sum():,.0f}"
    )
    print(
        f"Existing stations in modeled regions: "
        f"{regional_df['stations'].sum():,.0f}"
    )

    budget = 500
    result = solve_connector_allocation(regional_df, budget)
    checks, independent_min_cps = validate_solution(result)

    print(f"\nBudget: {budget}")
    print(
        f"Optimized minimum connectors/station: "
        f"{independent_min_cps:.6f}"
    )

    print("\nValidation:")
    for name, passed in checks.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")

    print("\nTop allocations:")
    print(
        result["allocation"]
        .sort_values("additional_connectors", ascending=False)
        .head(20)
        .to_string()
    )

    baseline = proportional_baseline(regional_df, budget)

    print("\nBaseline comparison:")
    print(
        f"  Proportional baseline minimum CPS: "
        f"{baseline['final_cps'].min():.6f}"
    )
    print(
        f"  Optimized minimum CPS: "
        f"{independent_min_cps:.6f}"
    )

    sensitivity, monotonic = validate_budget_sensitivity(
        regional_df,
        budgets=[100, 250, 500, 750, 1000],
    )

    print("\nBudget sensitivity:")
    print(sensitivity.to_string(index=False))
    print(
        f"\nMinimum-CPS monotonicity: "
        f"{'PASS' if monotonic else 'FAIL'}"
    )

    result["allocation"].to_csv(
        "optimization_2_allocation_500.csv"
    )
    sensitivity.to_csv(
        "optimization_2_budget_sensitivity.csv",
        index=False,
    )
