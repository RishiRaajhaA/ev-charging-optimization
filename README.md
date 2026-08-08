# EV Charging Infrastructure Optimization

## 1. Project Overview
This project presents an Operations Research approach to optimizing Electric Vehicle (EV) charging infrastructure. It leverages a dataset of existing EV charging stations to model and solve two distinct mathematical optimization problems: selecting high-capacity hub locations and fairly allocating new connectors across regions. The project includes data exploration, mathematical modeling, independent validation, and an interactive web interface.

## 2. Problem Statement
The expansion of EV charging infrastructure often occurs organically, leading to disparities in geographic coverage and regional infrastructure depth. Without assuming external factors such as power grid loads, population densities, or specific EV traffic patterns, this project addresses how to optimally expand the current infrastructure network using only the observed station locations and capacities.

## 3. Objectives
- Perform Exploratory Data Analysis (EDA) on the existing EV station dataset.
- Formulate and solve a Mixed-Integer Programming (MIP) model to maximize geographic coverage when placing new high-capacity charging hubs.
- Formulate and solve a max-min Mixed-Integer Linear Programming (MILP) model to allocate a budget of new connectors across regions, ensuring infrastructure fairness.
- Validate the mathematical integrity and correctness of the optimization models.
- Develop an interactive UI for users to explore the data and optimization results.

## 4. Dataset
The project utilizes `ev_stations_2025.csv`, which contains observed records of EV charging stations.
- **Records**: 10,000 stations
- **Total capacity**: 14,565 connectors
- **Relevant fields**: Latitude (`lat`), Longitude (`lon`), State/Region (`state`), Operational Status (`status`), Operator (`operator`), Number of Connectors (`num_connectors`).
- **Data Quality Issue**: 2,869 records are missing the `state` value.

## 5. Exploratory Data Analysis
EDA was conducted in Jupyter Notebook (`EDA.ipynb`) to understand the baseline infrastructure. 
**Key findings:**
- The network consists of 10,000 stations with 14,565 total connectors.
- The average station size is approximately 1.46 connectors per station.
- 96.18% of stations are classified as operational.
- The infrastructure is highly concentrated: the top 10% of stations contain 25.27% of all connectors.
- Geographically, Quebec (QC), British Columbia (BC), and Washington (WA) dominate, accounting for 34.34% of observed connectors.
- 2,869 records lack `state` administrative definitions, which requires special handling during regional modeling.

## 6. Methodology
The complete project pipeline follows a rigorous analytical workflow:

Dataset → EDA → Mathematical Formulation → Optimization → Validation → Streamlit UI

## 7. Optimization 1 — Charging Hub Location Selection
**Real-world question:** Where should we place a limited budget of new high-capacity charging hubs to maximize geographic coverage of existing smaller stations?
- **Candidate locations**: Generated from existing station coordinates using spherical K-means clustering.
- **Decision variables**: $y_j \in \{0, 1\}$ (Select candidate hub $j$).
- **Coverage variable**: $z_i \in \{0, 1\}$ (Station $i$ is covered).
- **Objective function**: Maximize $\sum z_i$ (Total number of covered stations).
- **Hub budget constraint**: $\sum y_j \le K$ (Maximum $K$ hubs).
- **Coverage constraint**: $z_i \le \sum_{j \in N_i} y_j$ (Station $i$ is covered only if at least one selected hub $j$ is within radius $R$).
- **Formulation**: Mixed-Integer Programming (MIP).

**Validated Example:**
- K = 10
- Radius = 50 km
- Covered stations = 3,278
- Coverage = 32.78%

The model was rigorously validated using sanity tests (e.g., zero hubs), K sensitivity, radius sensitivity, random baseline comparison, constraint checks, and independent objective calculation.

## 8. Optimization 2 — Regional Connector Allocation
**Real-world question:** Given a fixed budget of new connectors, how should they be allocated across regions to maximize the minimum regional connectors-per-station ratio?
- **Scope**: Valid-state regional scope. 7,131 included records (2,869 missing-state records were explicitly excluded).
- **Decision variable**: $x_i \ge 0$, integer (Additional connectors allocated to region $i$).
- **Connector budget**: Total budget constrained by $\sum x_i = B$.
- **Metric**: Connectors-per-station (CPS).
- **Objective**: Maximize $t$ (Minimum post-allocation CPS across all regions).
- **Fairness constraints**: $C_i + x_i \ge t \cdot S_i$ for all regions $i$.
- **Formulation**: Max-min Mixed-Integer Linear Programming (MILP).

**Validated Budget Sensitivity Results:**
| Budget | Minimum CPS |
|---:|---:|
| 100 | 1.000000 |
| 250 | 1.142857 |
| 500 | 1.212670 |
| 750 | 1.263441 |
| 1000 | 1.312375 |

The minimum CPS increased monotonically with the budget, and all independent mathematical validation checks passed successfully.

## 9. Model Validation
Both optimization models underwent separate, independent validation scripts to verify mathematical integrity.
- **Sanity Checks**: Ensuring logical extremes produce expected outputs (e.g. zero budget).
- **Sensitivity Analysis**: Confirming monotonic improvement when loosening constraints.
- **Baseline Comparisons**: Verifying solutions outperform random hub placement and proportional allocation baselines.
- **Constraint Validation**: Extracting the solver's decision variables and verifying they strictly adhere to bounds and logic.
- **Independent Objective Verification**: Recalculating the objective function outside of the solver environment to ensure correctness.

## 10. User Interface
The project features an interactive Streamlit application (`app.py`) with the following sections:
- **Dashboard**: High-level KPIs and project overview.
- **Data Explorer**: Interactive dataset filtering and preview.
- **Statistics**: Visualizations of state, operator, and geospatial distributions.
- **Optimization 1**: Interactive interface to run the Hub Location Selection model (User can select K and Radius).
- **Optimization 2**: Interactive interface to run the Regional Connector Allocation model (User can select budget).
- **Methodology**: Documentation of the mathematical formulations.

Optimization parameters can be dynamically selected by the user to explore different scenarios.

## 11. Technology Stack
- **Python**: Core programming language.
- **Pandas & NumPy**: Data manipulation and numerical operations.
- **SciPy** (`scipy.optimize.milp`): Solvers for Mixed-Integer Linear Programming.
- **Streamlit**: Web application framework for the UI.
- **Plotly**: Interactive data visualizations and mapping.
- **Jupyter Notebook**: Exploratory Data Analysis environment.

## 12. Project Structure
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
│       ├── optimization_1_validation_results.md
│       ├── optimization_2_validation_results.md
│       ├── validation_optimization_1.py
│       └── validation_optimization_2.py
└── outputs/
    └── maps/
        └── map_K10_R50.png
```

## 13. Installation
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

## 14. Running the Application
To start the Streamlit web application, run:
```bash
streamlit run app.py
```
**Accessing Optimizations**: Once the UI loads, navigate to "Optimization 1" or "Optimization 2" via the sidebar menu. Select your desired parameters using the sliders/dropdowns and click the "Run Optimization" button to trigger the models.

## 15. Reproducing Validation
The validation scripts can be executed directly from the project root to reproduce the mathematical verification reports.

For Optimization 1 (Hub Location):
```bash
python optimization/validation/validation_optimization_1.py
```
For Optimization 2 (Connector Allocation):
```bash
python optimization/validation/validation_optimization_2.py
```

## 16. Key Results
- The EDA revealed significant geographic and operator centralization within the network.
- Optimization 1 demonstrated that placing 10 high-capacity hubs at mathematically optimal locations covers 32.78% of the existing station network (at a 50km radius).
- Optimization 2 allocated regional budgets fairly, ensuring that the lowest-served region improved its connectors-per-station ratio monotonically as the investment budget increased.

## 17. Limitations
- **Missing State Values**: 2,869 records were excluded from regional modeling due to missing administrative identifiers.
- **Geographic Generation Assumptions**: Candidate hubs were generated via spherical clustering of existing stations rather than continuous geographic space.
- **Equal Weighting**: Optimization 1 treats all existing stations equally, ignoring current capacities or usage rates when calculating coverage.
- **Regional Metric**: Connectors-per-station is a simplified metric for infrastructure fairness.
- **Lack of External Data**: The model does not incorporate EV demand, population density, or traffic data.
- **Theoretical Scenarios**: The results represent mathematical optimization scenarios rather than real-world deployment recommendations.

## 18. Future Improvements
- **Demand and Population Integration**: Incorporating census data and EV registration density to weight the coverage objective.
- **Traffic Patterns**: Aligning candidate hubs with major highway traffic flow metrics.
- **Grid Constraints**: Modeling local electricity grid capacities as a constraint for hub placement.
- **Construction Costs**: Introducing variable installation costs by region or site complexity.
- **Detailed Geographic Modeling**: Expanding candidate generation to include continuous space or specific parcel availability.

## 19. Conclusion
This project successfully applied Operations Research methodologies to the problem of EV charging infrastructure expansion. Through rigorous Exploratory Data Analysis, we identified inherent network disparities. We subsequently formulated two Mixed-Integer Programming models to optimize geographic coverage and regional fairness. Supported by independent mathematical validation and packaged in an interactive web interface, this project demonstrates a robust, data-driven approach to infrastructure modeling.
