# Task: Perform Complete EDA for EV Charging Station Optimization Project

You are working on a university project involving **data analysis and mathematical optimization of EV charging station infrastructure**.

The dataset is:

`ev_stations_2025.csv`

It contains approximately 10,000 EV charging station records and the following columns:

* `id`
* `title`
* `address`
* `town`
* `state`
* `postcode`
* `country`
* `lat`
* `lon`
* `operator`
* `status`
* `num_connectors`
* `connector_types`
* `date_added`

Your task is to perform a **complete, rigorous Exploratory Data Analysis (EDA)** of this dataset.

## VERY IMPORTANT

This EDA is not being done just to create attractive graphs.

The main purpose is to determine:

1. What information is actually present in the dataset.
2. What patterns exist in the EV charging infrastructure.
3. What variables can reliably be used in mathematical optimization.
4. What optimization problems can realistically be formulated from this dataset.
5. What assumptions would be required for each potential optimization problem.

Do NOT invent variables such as EV traffic, charging demand, electricity consumption, revenue, population, vehicle count, or energy consumption because they are not directly present in the dataset.

If a proxy variable is proposed, clearly label it as a **derived proxy**, explain how it is calculated, and explain its limitations.

---

# 1. Set Up the EDA Environment

Create a clean Jupyter notebook:

`01_EDA_EV_Charging_Stations.ipynb`

Use Python.

Recommended libraries:

* pandas
* numpy
* matplotlib
* seaborn
* plotly
* scipy
* scikit-learn where genuinely useful
* geopandas only if necessary and available

Use appropriate plots and tables.

Make the notebook readable and organized with Markdown headings.

Do not create unnecessary visualizations just for the sake of having more plots.

---

# 2. Load and Inspect the Dataset

Load:

`ev_stations_2025.csv`

Display:

* Dataset shape
* First 5 rows
* Last 5 rows
* Column names
* Data types
* Dataset information
* Number of unique values per column
* Basic descriptive statistics

Clearly identify:

### Numerical variables

Examples:

* latitude
* longitude
* number of connectors

### Categorical variables

Examples:

* state
* town
* country
* operator
* status
* connector types

### Temporal variables

* date_added

Check whether `date_added` needs conversion to datetime.

---

# 3. Data Quality Analysis

Perform a thorough data-quality audit.

## 3.1 Missing Values

Create a table:

| Column | Missing Count | Missing % |
| ------ | ------------: | --------: |

Sort by missing percentage.

Explain which missing values matter for later analysis or optimization.

---

## 3.2 Duplicate Analysis

Check:

* Completely duplicated rows
* Duplicate IDs
* Duplicate combinations of latitude/longitude
* Potentially duplicated station records based on meaningful fields

Do NOT automatically delete duplicates.

First report them and explain whether they appear to be genuine duplicates.

---

## 3.3 Invalid Values

Check for:

### Geographic validity

Latitude must normally be:

`-90 <= latitude <= 90`

Longitude must normally be:

`-180 <= longitude <= 180`

Identify invalid coordinates.

### Connector validity

Check:

* minimum number of connectors
* zero connectors
* negative connectors
* extreme outliers

### Date validity

Check:

* invalid dates
* future dates
* unusually old dates

### Categorical consistency

Inspect unusual or inconsistent values in:

* status
* operator
* country
* state
* connector_types

---

# 4. Numerical Variable Analysis

For every important numerical variable, calculate:

* count
* mean
* median
* standard deviation
* minimum
* maximum
* Q1
* Q3
* IQR

Focus particularly on:

`num_connectors`

Create:

1. Histogram
2. Boxplot
3. Summary statistics table

Investigate whether the connector distribution is highly skewed.

Identify potential outliers using the IQR method.

Do NOT automatically remove outliers.

Explain whether outliers could represent legitimate large charging stations.

---

# 5. Categorical Variable Analysis

Analyze the major categorical variables.

## 5.1 Status

Show:

* count by status
* percentage by status
* bar chart

Determine the proportion of operational vs non-operational/other stations.

---

## 5.2 State

Show:

* number of stations by state
* percentage of total stations
* total connectors by state
* average connectors per station by state

Create suitable visualizations.

Identify:

* highest station-count regions
* lowest station-count regions
* highest connector-count regions
* regions with unusually high/low connectors per station

---

## 5.3 Operator

Analyze:

* number of stations by operator
* total connectors by operator
* average connectors per station by operator

Use a top-N visualization if there are many operators.

Do not hide the complete distribution from the analysis.

---

## 5.4 Connector Types

Analyze:

* most common connector types
* frequency of connector types
* connector-type combinations if the field contains multiple types

If the `connector_types` field contains multiple values in a single row, parse it carefully and report how this was handled.

---

# 6. Geographic EDA

This is a major part of the analysis.

Use:

* latitude
* longitude
* state
* town

## 6.1 Station Map

Create an interactive geographic visualization showing charging stations using latitude and longitude.

If there are too many points for a normal scatter plot, use an appropriate method such as:

* Plotly map
* density map
* hexbin
* clustering

Avoid producing a visualization that becomes unusable because of 10,000 overlapping points.

---

## 6.2 Geographic Distribution

Analyze:

* station concentration
* geographic clusters
* sparse areas
* station distribution by state
* connector distribution geographically

If appropriate, calculate approximate distances between stations using the Haversine formula.

Clearly document the distance calculation.

---

# 7. Station Density and Infrastructure Metrics

Create useful derived metrics.

At minimum investigate:

### Connectors per station

[
CPS_i =
\frac{\text{Total connectors}}
{\text{Number of stations}}
]

Calculate this at:

* overall level
* state level
* operator level where meaningful

---

### Operational station ratio

For each region:

[
OSR_i =
\frac{\text{Operational stations}}
{\text{Total stations}}
]

Use this only if the status categories can be reliably classified.

Clearly document which status values are treated as operational.

---

### Infrastructure share

For each state/region:

[
IS_i =
\frac{\text{Connectors in region }i}
{\text{Total connectors}}
]

Analyze whether infrastructure is concentrated in a small number of regions.

---

# 8. Temporal Analysis

Convert `date_added` into datetime if necessary.

Analyze:

* stations added per year
* stations added per month/year where meaningful
* cumulative stations over time
* cumulative connectors over time if appropriate

Answer:

* Is the dataset showing infrastructure growth?
* Are there periods with unusually high station additions?
* Are there obvious data-collection artifacts?

Be careful not to interpret `date_added` as actual construction date unless the dataset definition supports that.

---

# 9. Bivariate Analysis

Investigate relationships between important variables.

At minimum analyze:

### State vs number of connectors

### State vs average connectors per station

### State vs operational ratio

### Operator vs number of connectors

### Operator vs average connectors per station

### Status vs number of connectors

### Date added vs number of connectors

Use appropriate visualizations such as:

* grouped bar charts
* boxplots
* scatter plots
* heatmaps
* correlation matrices where meaningful

Do not calculate correlations for arbitrary categorical variables.

---

# 10. Outlier and Distribution Analysis

Investigate whether a small number of stations dominate the infrastructure.

Questions to answer:

* What percentage of stations contain the top 10% of connectors?
* Are there extremely large stations?
* Does a small group of states contain a disproportionate number of connectors?
* Does a small group of operators control a large portion of infrastructure?

These findings are potentially important for resource-allocation optimization.

---

# 11. Feature Engineering for Optimization

Create a separate section for variables that could potentially be useful in optimization.

Possible derived features include:

* `connectors_per_station`
* `operational_ratio`
* `station_count_by_region`
* `connector_count_by_region`
* `infrastructure_share`
* `station_density` if an appropriate geographic denominator is available
* geographic distance measures
* station-age-related variables

For every derived variable, document:

1. Formula
2. Meaning
3. Why it may be useful
4. Limitations

Do not create arbitrary scores without justification.

---

# 12. Identify Infrastructure Imbalances

This section is extremely important.

Analyze whether there are measurable infrastructure imbalances between regions.

For each state/region, create a summary table containing, where available:

| Region | Stations | Connectors | Avg Connectors/Station | Operational Ratio | Infrastructure Share |
| ------ | -------: | ---------: | ---------------------: | ----------------: | -------------------: |

Then identify:

* highly concentrated regions
* infrastructure-poor regions according to measurable dataset variables
* regions with high station count but low connectors/station
* regions with low station count but relatively high connectors/station
* regions with poor operational ratios

Do NOT call a region "underserved" unless the metric used to define that term is explicitly stated.

Prefer wording such as:

> "The region has relatively low charging infrastructure according to the selected metric."

---

# 13. Correlation / Statistical Analysis

Calculate correlations only for meaningful numerical variables.

Investigate relationships among:

* latitude
* longitude
* num_connectors
* derived numerical features

For categorical variables, use appropriate statistical techniques if useful.

The goal is not to perform advanced statistics unnecessarily, but to discover relationships that could influence optimization.

---

# 14. EDA Findings

At the end of the notebook, create a section:

# Key EDA Findings

Summarize approximately 8–15 important findings.

Each finding should be specific and supported by an actual result.

Bad:

> "There are differences between states."

Good:

> "State X contains approximately Y% of all stations while accounting for Z% of all connectors, indicating a difference between station share and connector share."

Do not invent values. Calculate them from the dataset.

---

# 15. Optimization Opportunity Discovery

This is the MOST IMPORTANT final section.

Based on the actual EDA results, propose **at least 5 candidate optimization problems**.

For each candidate, provide:

| Candidate | Optimization Question | Decision Variables | Objective | Constraints | Required Data | Difficulty |
| --------- | --------------------- | ------------------ | --------- | ----------- | ------------- | ---------- |

Potential directions to investigate include:

### Candidate A — Regional Connector Allocation

Given a fixed number of additional connectors, determine how they should be allocated across regions.

Potential objective:

* improve infrastructure balance
* maximize a clearly defined infrastructure score
* minimize regional disparity

---

### Candidate B — Charging Station Location Selection

Given a fixed number of new stations, identify candidate locations that maximize geographic coverage or minimize distance to existing infrastructure.

This may require clustering or candidate-location generation.

---

### Candidate C — Infrastructure Balancing

Determine how resources should be allocated to reduce disparity in charging infrastructure across regions.

Possible objective:

* minimize variance
* minimize maximum-minimum disparity
* maximize minimum regional infrastructure level

---

### Candidate D — Connector Allocation Under Constraints

Determine how connectors should be allocated while satisfying constraints such as:

* fixed total connectors
* regional limits
* minimum/maximum allocation
* operational considerations

---

### Candidate E — Geographic Coverage Optimization

Select a limited number of candidate locations to maximize coverage of existing station clusters or minimize average distance.

Do not assume population or traffic demand.

---

# 16. Score the Candidate Optimization Problems

Create a final table scoring each candidate from 1–10 on:

| Criterion                      | Score |
| ------------------------------ | ----: |
| Dataset support                |   /10 |
| Mathematical formulation       |   /10 |
| Optimization relevance         |   /10 |
| Course technique compatibility |   /10 |
| UI suitability                 |   /10 |
| Result interpretability        |   /10 |
| Implementation difficulty      |   /10 |
| Presentation/demo value        |   /10 |

Then calculate an overall score.

Recommend the **top 3 optimization problems**.

Do NOT automatically choose LP/IP just because they are easy.

The optimization method should be selected after the mathematical problem is understood.

---

# 17. Recommended Optimization Techniques

After identifying the top optimization problems, recommend which techniques from the following categories would fit them:

* Linear Programming
* Quadratic Programming
* Integer Programming
* Mixed Integer Programming
* Convex Optimization
* Other optimization techniques that are actually appropriate

For each recommendation explain:

1. Why the technique fits.
2. Whether the objective is linear/nonlinear.
3. Whether variables need to be continuous/integer/binary.
4. Whether constraints are linear/nonlinear.
5. What solver/library could implement it.

Do not force a technique onto a problem.

---

# 18. Important Restrictions

Follow these rules throughout the analysis:

### Do not fabricate data.

Every numerical result must come from the CSV.

### Do not assume demand.

The dataset does not directly measure:

* EV traffic
* charging demand
* electricity consumption
* revenue
* population
* vehicle ownership

Do not present these as if they exist.

### Do not delete data silently.

Every cleaning decision must be documented.

### Do not overuse plots.

Every visualization must answer a question.

### Do not over-engineer.

The goal is to prepare this dataset for a university optimization project.

---

# 19. Final Notebook Structure

The final notebook should contain:

```text
01. Project Introduction
02. Dataset Loading
03. Dataset Overview
04. Data Quality Analysis
05. Numerical Analysis
06. Categorical Analysis
07. Geographic Analysis
08. Temporal Analysis
09. Bivariate Analysis
10. Outlier Analysis
11. Feature Engineering
12. Infrastructure Imbalance Analysis
13. Key EDA Findings
14. Candidate Optimization Problems
15. Optimization Problem Scoring
16. Recommended Optimization Problems
17. Recommended Optimization Techniques
18. Conclusion
```

---

# 20. Final Conclusion

End the notebook with a concise conclusion answering:

1. What does the dataset contain?
2. What are the most important patterns?
3. What data-quality issues exist?
4. What infrastructure imbalances exist?
5. Which variables are suitable for optimization?
6. What are the top 3 optimization problems?
7. Which 2 optimization problems are recommended for the final project?
8. Which optimization techniques are most appropriate for those problems?

The final recommendation must be **evidence-based on the actual EDA results**.

The ultimate goal is to move from:

**Dataset → EDA → Evidence → Optimization Problem → Mathematical Formulation → Optimization Technique**

Do not start implementing the optimization algorithms yet.

First complete the EDA and identify the strongest optimization problems.
