# EV Charging Infrastructure Optimization

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)

> Interactive EV infrastructure analysis and optimization using two mathematical optimization models.

This project applies Operations Research methodologies and Mixed-Integer Programming to optimize the expansion of Electric Vehicle (EV) charging infrastructure based on a real-world dataset.

---

## 1. Project Overview

> Given an existing EV charging network and limited resources, where should new charging hubs be placed and how should additional connectors be allocated across regions?

To answer this, the project features:
- In-depth Exploratory Data Analysis (EDA)
- Two distinct mathematical optimization models
- Rigorous independent validation of results
- An interactive Streamlit User Interface allowing users to upload their own datasets and run scenario testing

---

## 2. Key Results

| Metric | Result |
|---|---:|
| Charging Stations | 10,000 |
| Connectors | 14,565 |
| Operational Classification | 96.18% |
| Valid Regional Records | 7,131 |
| Optimization 1 Coverage | 3,278 stations / 32.78% |
| Optimization 2 Budget Example | 500 connectors → 1.212670 minimum CPS |

---

## 3. Operations Research Concepts Applied

This project maps directly to core Operations Research syllabus concepts:
- **Integer Programming** (IP and MILP)
- **Facility Location / Maximum Coverage**
- **Resource Allocation**
- **Max-Min Optimization** (Fairness)
- **Sensitivity Analysis**

---

## 4. Optimization Problems

### Optimization 1 — Charging Hub Location

> Where should a limited number of new charging hubs be placed to maximize coverage of existing stations?

This problem is formulated using **Mixed-Integer Programming (MIP)**:
- **Candidate Hubs**: Generated via spherical K-means clustering to ensure hubs are evaluated at realistic coordinate clusters.
- **Decision Variable ($y_j$)**: Binary variable indicating whether a candidate hub is selected.
- **Coverage Variable ($z_i$)**: Binary variable indicating whether an existing station is covered.
- **Constraint 1 (Maximum Hubs)**: The total number of selected hubs cannot exceed the budget ($K$).
- **Constraint 2 (Coverage Radius)**: A station is only covered if a selected hub is within the defined coverage radius.

**Example Scenario (Using sample dataset):**
- K = 10 hubs
- Radius = 50 km
- Covered = 3,278 stations
- Coverage = 32.78%

### Optimization 2 — Regional Connector Allocation

> How should a fixed number of additional connectors be distributed across regions to maximize the minimum connectors-per-station ratio?

This problem is formulated using **Max-Min Mixed-Integer Linear Programming (MILP)**:
- **Decision Variable ($x_i$)**: Integer allocation of new connectors to region $i$.
- **Budget Constraint**: Total allocated connectors cannot exceed the strict connector budget.
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
4. **Optimization**: Solving the equations computationally.
5. **Independent Validation**: Programmatically verifying the solver outputs against raw data and randomized baselines.
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
- **Random Baseline Comparison**: The optimization consistently outperforms a randomized baseline of 100 trials, selecting the same $K$ hubs.

**Optimization 2 Validation:**
- Budget sensitivity
- **Proportional Baseline Comparison**: The max-min equity objective significantly outperforms naive proportional allocation for raising the floor of the network's worst-off regions.
- Fairness constraint validation

---

## 8. Interactive Application

The project features a comprehensive Streamlit UI, allowing users to upload CSVs, dynamically change optimization parameters, and run scenarios interactively.

The application includes:
- **Data Source**: A robust CSV uploader that parses and validates required column data.
- **Dashboard**: High-level metrics.
- **Data Explorer**: Interactive dataframe filtering.
- **Statistics**: Exact descriptive statistics and visual geospatial distribution charts.
- **Optimization Center**: A consolidated hub for running both Optimization 1 and Optimization 2.
- **Methodology**: Documentation of the models.

## Application Screenshots

*(No screenshots are currently provided in the repository.)*

---

## 9. Dataset

**Source:** [Manual Confirmation Required: Add exact public dataset source, e.g., US DOE Alternative Fuels Data Center, Kaggle, etc.]

**License:** [Manual Confirmation Required: Determine dataset original license]

The sample dataset (`data/ev_stations_2025.csv`) represents observed EV charging stations with fields including:
- `lat`: Latitude
- `lon`: Longitude
- `state`: Regional administrative identifier
- `status`: Operational status
- `operator`: Managing company
- `num_connectors`: Number of physical charging connectors

> **Note:** 2,869 records have missing `state` values. These records are explicitly excluded from the regional Optimization 2 scope.

---

## 10. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| Pandas | Data processing |
| NumPy | Numerical computation |
| SciPy | MILP/MIP optimization (`scipy.optimize.milp`) |
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

---

## 12. Installation

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment (Windows):
   ```bash
   .venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 13. Usage

To start the Streamlit web application, run:
```bash
streamlit run app.py
```
**Accessing Optimizations**: Once the UI loads, navigate to the **Optimization Center** via the sidebar menu. Choose your desired mathematical model, adjust parameters, and click the execution button to trigger the solvers. You can also upload your own valid EV dataset from the sidebar.

---

## 14. Limitations

- **Missing State Values**: 2,869 records were excluded from regional modeling due to missing administrative identifiers.
- **Geographic Generation Assumptions**: Candidate hubs were generated via spherical clustering of existing stations rather than continuous geographic space.
- **Equal Weighting**: Optimization 1 treats all existing stations equally, ignoring current capacities or usage rates when calculating coverage.
- **Regional Metric**: Connectors-per-station is a simplified metric for infrastructure fairness.
- **Lack of External Data**: The model does not incorporate EV demand, population density, or traffic data.
- **Theoretical Scenarios**: The results represent mathematical optimization scenarios rather than real-world deployment recommendations.

---

## 15. Future Work

- **Demand and Population Integration**: Incorporating census data and EV registration density to weight the coverage objective.
- **Traffic Patterns**: Aligning candidate hubs with major highway traffic flow metrics.
- **Grid Constraints**: Modeling local electricity grid capacities as a constraint for hub placement.
- **Construction Costs**: Introducing variable installation costs by region or site complexity.
- **Detailed Geographic Modeling**: Expanding candidate generation to include continuous space or specific parcel availability.

---

## 16. References

- Optimization solver reference: `scipy.optimize.milp` (SciPy Documentation)
- Web framework reference: Streamlit Documentation
- Foundational Operations Research methodologies: Facility Location Problem, Max-Min Fairness, Resource Allocation
