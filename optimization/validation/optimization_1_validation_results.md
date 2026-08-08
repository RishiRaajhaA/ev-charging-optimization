# Optimization 1 Validation Results

## A. Configuration

- **Dataset**: D:\Operations Research\data\ev_stations_2025.csv
- **Number of stations**: 10000
- **Number of valid coordinates**: 10000
- **Candidate locations**: 100
- **Solver**: scipy.optimize.milp

## B. Sanity Test Results

| Test | Expected | Actual | Status |
|---|---|---|---|
| Test A (K=0, r=50) | 0 hubs, 0 coverage | 0 hubs, 0 coverage | PASS |
| Test B (K=1, r=10000) | 1 hub, >98% coverage | 1 hubs, 9871 coverage | PASS |
| Test C (K=10, r=0.1) | low coverage | 0.15% coverage | PASS |

## C. K-Sensitivity Results

Fixed radius = 50 km

| K | Selected Hubs | Covered Stations | Coverage % |
|---|---:|---:|---:|
| 5 | 5 | 2631 | 26.31% |
| 10 | 10 | 3278 | 32.78% |
| 20 | 20 | 3815 | 38.15% |
| 30 | 30 | 4059 | 40.59% |

Monotonicity Check (Coverage increases with K): **PASS**

## D. Radius-Sensitivity Results

Fixed K = 10

| Radius (km) | Covered Stations | Coverage % |
|---:|---:|---:|
| 10 | 559 | 5.59% |
| 25 | 2313 | 23.13% |
| 50 | 3278 | 32.78% |
| 75 | 3778 | 37.78% |
| 100 | 4197 | 41.97% |

Monotonicity Check (Coverage increases with radius): **PASS**

## E. Baseline Comparison

Fixed K = 10, Radius = 50 km

| Method | Mean Coverage | Std Dev | Min | Max |
|---|---:|---:|---:|---:|
| Random baseline | 474.7 | 454.1 | 39 | 1996 |
| MIP | 3278 | N/A | 3278 | 3278 |

MIP outperforms random baseline: **PASS**

MIP achieves an improvement of 590.5% over the random baseline.

## F. Constraint Validation

Checking MIP mathematical solution validity for K=10, R=50:

- **Constraint 4 (Binary decisions)**: PASS
- **Constraint 1 (Hub budget)**: 10.0 <= 10 -> PASS
- **Constraint 2 (Coverage validity)**: PASS
- **Constraint 3 (Uncovered stations)**: PASS
- **Constraint 5 (Independent objective calculation)**: Calculated 3278 vs Solver 3278 -> PASS

## G. Geographic Validation

Generated visualization saved to `D:\Operations Research\outputs\maps\map_K10_R50.png`.

## H. Overall Verdict

```text
Optimization 1 Validation Status: PASS
```
