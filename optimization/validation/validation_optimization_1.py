import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from optimization.optimization_1_hub_location import generate_candidate_hubs, solve_max_coverage, haversine_matrix

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "ev_stations_2025.csv"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs" / "maps"
REPORT_PATH = Path(__file__).parent / "optimization_1_validation_results.md"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- Load Data ---
print("Loading data...")
df = pd.read_csv(DATA_PATH)
candidates = generate_candidate_hubs(df, n_candidates=100, random_state=42)

valid_df = df.dropna(subset=['lat', 'lon']).copy().reset_index(drop=True)
n_valid = len(valid_df)

report_lines = []
report_lines.append("# Optimization 1 Validation Results\n")
report_lines.append("## A. Configuration\n")
report_lines.append(f"- **Dataset**: {DATA_PATH}")
report_lines.append(f"- **Number of stations**: {len(df)}")
report_lines.append(f"- **Number of valid coordinates**: {n_valid}")
report_lines.append(f"- **Candidate locations**: {len(candidates)}")
report_lines.append("- **Solver**: scipy.optimize.milp\n")

passed_tests = []
failed_tests = []

def record_test(name, is_pass, msg=""):
    status = "PASS" if is_pass else "FAIL"
    if is_pass:
        passed_tests.append(name)
    else:
        failed_tests.append(f"{name} ({msg})" if msg else name)
    return status

print("Running Sanity Tests...")
# --- B. Sanity Tests ---
report_lines.append("## B. Sanity Test Results\n")
report_lines.append("| Test | Expected | Actual | Status |")
report_lines.append("|---|---|---|---|")

# Test A
res_A = solve_max_coverage(df, candidates, n_hubs=0, radius_km=50)
pass_A = (res_A['n_hubs'] == 0 and res_A['covered_stations'] == 0)
report_lines.append(f"| Test A (K=0, r=50) | 0 hubs, 0 coverage | {res_A['n_hubs']} hubs, {res_A['covered_stations']} coverage | {record_test('Sanity A', pass_A)} |")

# Test B
res_B = solve_max_coverage(df, candidates, n_hubs=1, radius_km=10000)
pass_B = (res_B['n_hubs'] == 1 and res_B['covered_stations'] >= n_valid * 0.98)
report_lines.append(f"| Test B (K=1, r=10000) | 1 hub, >98% coverage | {res_B['n_hubs']} hubs, {res_B['covered_stations']} coverage | {record_test('Sanity B', pass_B)} |")

# Test C
res_C = solve_max_coverage(df, candidates, n_hubs=10, radius_km=0.1)
pass_C = (res_C['n_hubs'] <= 10 and res_C['coverage_rate'] < 0.05) # Expected very low
report_lines.append(f"| Test C (K=10, r=0.1) | low coverage | {res_C['coverage_rate']:.2%} coverage | {record_test('Sanity C', pass_C)} |\n")

print("Running K-Sensitivity Tests...")
# --- C. K-Sensitivity Tests ---
report_lines.append("## C. K-Sensitivity Results\n")
report_lines.append("Fixed radius = 50 km\n")
report_lines.append("| K | Selected Hubs | Covered Stations | Coverage % |")
report_lines.append("|---|---:|---:|---:|")

k_results = []
for k in [5, 10, 20, 30]:
    res = solve_max_coverage(df, candidates, n_hubs=k, radius_km=50)
    k_results.append(res['covered_stations'])
    report_lines.append(f"| {k} | {res['n_hubs']} | {res['covered_stations']} | {res['coverage_rate']:.2%} |")

k_monotonic = all(k_results[i] <= k_results[i+1] for i in range(len(k_results)-1))
report_lines.append(f"\nMonotonicity Check (Coverage increases with K): **{record_test('K-Sensitivity Monotonicity', k_monotonic)}**\n")

print("Running Radius-Sensitivity Tests...")
# --- D. Radius-Sensitivity Tests ---
report_lines.append("## D. Radius-Sensitivity Results\n")
report_lines.append("Fixed K = 10\n")
report_lines.append("| Radius (km) | Covered Stations | Coverage % |")
report_lines.append("|---:|---:|---:|")

r_results = []
for r in [10, 25, 50, 75, 100]:
    res = solve_max_coverage(df, candidates, n_hubs=10, radius_km=r)
    r_results.append(res['covered_stations'])
    report_lines.append(f"| {r} | {res['covered_stations']} | {res['coverage_rate']:.2%} |")

r_monotonic = all(r_results[i] <= r_results[i+1] for i in range(len(r_results)-1))
report_lines.append(f"\nMonotonicity Check (Coverage increases with radius): **{record_test('Radius-Sensitivity Monotonicity', r_monotonic)}**\n")

print("Running Baseline Comparison...")
# --- E. Baseline Comparison ---
report_lines.append("## E. Baseline Comparison\n")
report_lines.append("Fixed K = 10, Radius = 50 km\n")
report_lines.append("| Method | Mean Coverage | Std Dev | Min | Max |")
report_lines.append("|---|---:|---:|---:|---:|")

# Random Baseline
np.random.seed(42)
candidate_coords = candidates[['lat', 'lon']].to_numpy()
station_coords = valid_df[['lat', 'lon']].to_numpy()
distances = haversine_matrix(station_coords, candidate_coords)

random_coverages = []
for _ in range(100):
    selected = np.random.choice(len(candidates), 10, replace=False)
    min_dist = np.min(distances[:, selected], axis=1)
    covered = np.sum(min_dist <= 50)
    random_coverages.append(covered)

random_mean = np.mean(random_coverages)
random_std = np.std(random_coverages)
random_min = np.min(random_coverages)
random_max = np.max(random_coverages)

mip_res = solve_max_coverage(df, candidates, n_hubs=10, radius_km=50)
mip_coverage = mip_res['covered_stations']

report_lines.append(f"| Random baseline | {random_mean:.1f} | {random_std:.1f} | {random_min} | {random_max} |")
report_lines.append(f"| MIP | {mip_coverage} | N/A | {mip_coverage} | {mip_coverage} |")

pass_baseline = mip_coverage > random_mean
report_lines.append(f"\nMIP outperforms random baseline: **{record_test('Baseline Comparison', pass_baseline)}**\n")
if pass_baseline:
    report_lines.append(f"MIP achieves an improvement of {(mip_coverage - random_mean)/random_mean:.1%} over the random baseline.\n")

print("Running Constraint Validation...")
# --- F. Constraint Validation ---
report_lines.append("## F. Constraint Validation\n")
report_lines.append("Checking MIP mathematical solution validity for K=10, R=50:\n")

sol = mip_res['solver_result']
n_cand = len(candidates)

y_vars = sol.x[:n_cand]
z_vars = sol.x[n_cand:]
is_binary = np.all(np.isclose(y_vars, np.round(y_vars))) and np.all(np.isclose(z_vars, np.round(z_vars)))
c4_pass = is_binary
report_lines.append(f"- **Constraint 4 (Binary decisions)**: {record_test('Constraint 4 Binary', c4_pass)}")

num_selected = np.sum(np.round(y_vars))
c1_pass = num_selected <= 10
report_lines.append(f"- **Constraint 1 (Hub budget)**: {num_selected} <= 10 -> {record_test('Constraint 1 Budget', c1_pass)}")

selected_indices = np.where(np.round(y_vars) == 1)[0]
if len(selected_indices) > 0:
    min_dist = np.min(distances[:, selected_indices], axis=1)
else:
    min_dist = np.full(len(valid_df), np.inf)
actual_covered = min_dist <= 50

neighbors = [np.flatnonzero(row <= 50) for row in distances]
covered_rows = [i for i, candidate_neighbors in enumerate(neighbors) if len(candidate_neighbors) > 0]

solver_covered = np.zeros(len(valid_df), dtype=bool)
for row_idx, station_idx in enumerate(covered_rows):
    if np.round(z_vars[row_idx]) == 1:
        solver_covered[station_idx] = True

c2_pass = True
for idx in np.where(solver_covered)[0]:
    if min_dist[idx] > 50:
        c2_pass = False
        break
report_lines.append(f"- **Constraint 2 (Coverage validity)**: {record_test('Constraint 2 Validity', c2_pass)}")

c3_pass = True
for idx in np.where(~solver_covered)[0]:
    if min_dist[idx] <= 50:
        c3_pass = False
        break
report_lines.append(f"- **Constraint 3 (Uncovered stations)**: {record_test('Constraint 3 Uncovered', c3_pass)}")

calc_coverage = int(np.sum(actual_covered))
calc_coverage_rate = calc_coverage / len(valid_df)
c5_pass = (calc_coverage == mip_res['covered_stations']) and np.isclose(calc_coverage_rate, mip_res['coverage_rate'])
report_lines.append(f"- **Constraint 5 (Independent objective calculation)**: Calculated {calc_coverage} vs Solver {mip_res['covered_stations']} -> {record_test('Constraint 5 Obj Calc', c5_pass)}\n")

print("Generating Geographic Visualization...")
# --- G. Geographic Validation ---
report_lines.append("## G. Geographic Validation\n")
map_path = os.path.join(OUTPUT_DIR, "map_K10_R50.png")
report_lines.append(f"Generated visualization saved to `{map_path}`.\n")

plt.figure(figsize=(12, 8))
plt.scatter(valid_df['lon'], valid_df['lat'], s=1, color='gray', alpha=0.5, label='Existing Stations')

selected_hubs = candidates.iloc[selected_indices]
plt.scatter(selected_hubs['lon'], selected_hubs['lat'], s=50, color='red', marker='*', label='Selected Hubs')

for _, row in selected_hubs.iterrows():
    lat_deg = row['lat']
    lon_deg = row['lon']
    r_lat = 50 / 111.0
    r_lon = 50 / (111.0 * np.cos(np.radians(lat_deg)))
    circle = plt.matplotlib.patches.Ellipse((lon_deg, lat_deg), r_lon*2, r_lat*2, color='blue', alpha=0.2)
    plt.gca().add_patch(circle)

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Optimization 1: Selected Hubs and Coverage (K=10, R=50km)")
plt.legend()
plt.savefig(map_path)
plt.close()

# --- H. Overall Verdict ---
report_lines.append("## H. Overall Verdict\n")
all_passed = len(failed_tests) == 0
if all_passed:
    report_lines.append("```text\nOptimization 1 Validation Status: PASS\n```\n")
else:
    report_lines.append("```text\nOptimization 1 Validation Status: FAIL\n```\n")
    report_lines.append(f"Failed tests: {', '.join(failed_tests)}\n")

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write("\n".join(report_lines))

print("\n--- Validation Summary ---")
print(f"Passed tests: {len(passed_tests)}")
print(f"Failed tests: {len(failed_tests)}")
if failed_tests:
    print("FAILED:")
    for f in failed_tests:
        print(f" - {f}")
print(f"Optimization 1 Validation Status: {'PASS' if all_passed else 'FAIL'}")
