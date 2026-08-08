# Optimization 2 Validation Results

## A. Configuration

- **Dataset**: ev_stations_2025.csv
- **Total Dataset Records**: 10,000
- **Records with Valid State (Included)**: 7,131
- **Records with Missing State (Excluded)**: 2,869
- **Decision Variable**: Integer additional connectors allocated to each state
- **Solver**: `scipy.optimize.milp`

## B. Budget Sensitivity & Monotonicity (Min-CPS)

| Budget | Minimum CPS | Total Allocated | Constraints Passed |
|---:|---:|---:|---|
| 100 | 1.000000 | 100 | PASS |
| 250 | 1.142857 | 250 | PASS |
| 500 | 1.212670 | 500 | PASS |
| 750 | 1.263441 | 750 | PASS |
| 1000 | 1.312375 | 1000 | PASS |

Monotonicity Check (Min-CPS increases with Budget): **PASS**

## C. Baseline Comparison (Proportional vs. Optimized)

Testing across all budgets:

| Budget | Proportional Baseline Min CPS | Optimized Min CPS | Improved? |
|---:|---:|---:|---|
| 100 | 0.000000 | 1.000000 | PASS |
| 250 | 0.000000 | 1.142857 | PASS |
| 500 | 0.000000 | 1.212670 | PASS |
| 750 | 0.000000 | 1.263441 | PASS |
| 1000 | 0.000000 | 1.312375 | PASS |

Optimization performs >= Baseline across all budgets: **PASS**

## D. Detailed Constraint Validation (Budget = 500)

- **budget**: PASS
- **integer_nonnegative**: PASS
- **objective_match**: PASS
- **fairness_constraints**: PASS

## E. Overall Verdict

```text
Optimization 2 Validation Status: PASS
```
