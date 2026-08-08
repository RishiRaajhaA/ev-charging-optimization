# EV Charging Infrastructure Optimization

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)

> Interactive EV infrastructure analysis and optimization using two mathematical optimization models.

This project applies Operations Research methodologies and Mixed-Integer Programming to optimize the expansion of Electric Vehicle (EV) charging infrastructure based on a real-world dataset.

---

## 2. Project Overview

Given an existing EV charging network and limited resources, where should new charging hubs be placed and how should additional connectors be allocated across regions?

To answer this, the project features:
- In-depth Exploratory Data Analysis (EDA)
- Two distinct mathematical optimization models
- Rigorous independent validation of results
- An interactive Streamlit User Interface for scenario testing

---

## 3. Key Results

| Metric | Result |
|---|---:|
| Charging Stations | 10,000 |
| Connectors | 14,565 |
| Operational Classification | 96.18% |
| Valid Regional Records | 7,131 |
| Optimization 1 Coverage | 3,278 stations / 32.78% |
| Optimization 2 Budget Example | 500 connectors → 1.212670 minimum CPS |

---

## 4. Optimization Problems

### Optimization 1 — Charging Hub Location

> Where should a limited number of new charging hubs be placed to maximize coverage of existing stations?

This problem is formulated using **Mixed-Integer Programming (MIP)**:
- **Candidate Hubs**: Generated via spherical K-means clustering.
- **Decision Variable ($y_j$)**: Binary variable indicating whether a candidate hub is selected.
- **Coverage Variable ($z_i$)**: Binary variable indicating whether a station is covered.
- **Constraint 1 (Maximum Hubs)**: The total number of selected hubs cannot exceed the budget ($K$).
- **Constraint 2 (Coverage Radius)**: A station is only covered if a selected hub is within the defined radius.

**Example Scenario:**
- K = 10
- Radius = 50 km
- Covered = 3,278
- Coverage = 32.78%

### Optimization 2 — Regional Connector Allocation

> How should a fixed number of additional connectors be distributed across regions to maximize the minimum connectors-per-station ratio?

This problem is formulated using **Max-Min Mixed-Integer Linear Programming (MILP)**:
- **Decision Variable ($x_i$)**: Integer allocation of new connectors to region $i$.
- **Budget Constraint**: Total allocated connectors cannot exceed the connector budget.
- **Metric**: Connectors-per-station (CPS).
- **Objective**: Maximize the minimum CPS across all regions.
- **Fairness Constraint**: Post-allocation CPS for every region must be greater than or equal to the target minimum.

**Budget vs. Minimum CPS:**

| Budget | Minimum CPS |
|---:|---:|
| 100 | 1.000000 |
| 250 | 1.142857 |
| 500 | 1.212670 |
| 750 | 1.263441 |
| 1000 | 1.312375 |

---

## 5. EDA Highlights

- **10,000 stations** with **14,565 connectors** in total.
- The average is **~1.46 connectors/station**.
- **96.18%** operational classification.
- The infrastructure is highly concentrated: the **top 10% of stations contain 25.27% of connectors**.
- **QC, BC and WA** account for **34.34%** of observed connectors.
- **2,869 records** have missing state values.

---

## 6. Methodology

Dataset
↓
EDA
↓
Mathematical Formulation
↓
Optimization
↓
Independent Validation
↓
Interactive Streamlit UI

1. **Dataset**: Raw EV station records.
2. **EDA**: Identifying patterns, biases, and missing data points.
3. **Mathematical Formulation**: Translating the business problems into strict mathematical equations.
4. **Optimization**: Solving the equations using `scipy.optimize.milp`.
5. **Independent Validation**: Programmatically verifying the solver outputs against raw data and baselines.
6. **Interactive Streamlit UI**: Presenting the models dynamically to the user.

---

## 7. Validation

Both optimization models were rigorously and independently validated to ensure mathematical integrity using:
- Sanity checks
- Sensitivity analysis
- Baseline comparisons
- Constraint validation
- Independent objective verification

**Optimization 1 Validation:**
- K sensitivity
- Radius sensitivity
- Random baseline comparison

**Optimization 2 Validation:**
- Budget sensitivity
- Proportional baseline comparison
- Fairness constraint validation

---

## 8. Interactive Application

The project features a comprehensive Streamlit UI, allowing users to dynamically change optimization parameters and run scenarios interactively.

The application includes:
- **Dashboard**: High-level metrics.
- **Data Explorer**: Interactive dataframe filtering.
- **Statistics**: Geopolitical and operator distribution graphs.
- **Optimization 1**: Interactive Hub Location runner.
- **Optimization 2**: Interactive Regional Allocation runner.
- **Methodology**: Documentation of the models.

## Application Preview

*(Screenshots of the interactive application can be placed here.)*

---

## 9. Dataset

The dataset represents observed EV charging stations with fields including:
- `lat`: Latitude
- `lon`: Longitude
- `state`: Regional administrative identifier
- `status`: Operational status
- `operator`: Managing company
- `num_connectors`: Number of physical charging connectors

> 2,869 records have missing `state` values and are excluded from the regional optimization scope.

---

## 10. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| Pandas | Data processing |
| NumPy | Numerical computation |
| SciPy | MILP/MIP optimization |
| Streamlit | Interactive UI |
| Plotly | Interactive visualization |
| Jupyter | EDA |

---

## 11. Project Structure

```text
Operations Research/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── ev_stations_2025.csv
├── eda/
│   ├── EDA.ipynb
│   └── EDA_Process.md
├── optimization/
│   ├── optimization_1_hub_location.py
│   ├── optimization_2_connector_allocation.py
│   └── validation/
│       ├── validation_optimization_1.py
│       ├── validation_optimization_2.py
│       ├── optimization_1_validation_results.md
│       └── optimization_2_validation_results.md
└── outputs/
    └── maps/
        └── map_K10_R50.png
```
