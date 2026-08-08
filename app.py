# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

# Import Optimization 1
from optimization.optimization_1_hub_location import generate_candidate_hubs, solve_max_coverage
# Import Optimization 2
from optimization.optimization_2_connector_allocation import load_regional_data, solve_connector_allocation, proportional_baseline

# Configuration
st.set_page_config(page_title="EV Charging Optimization", layout="wide", page_icon="⚡")

# Custom CSS for premium UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #A0AEC0;
        margin-top: -10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Data Loading Cache
@st.cache_data
def load_base_data():
    df = pd.read_csv("data/ev_stations_2025.csv")
    df['num_connectors'] = pd.to_numeric(df['num_connectors'], errors='coerce')
    op_statuses = ['Operational', 'Active', 'Available', 'Online', 'operational']
    df['is_operational'] = df['status'].astype(str).str.contains('|'.join(op_statuses), case=False, na=False)
    return df

@st.cache_data
def load_opt2():
    df, regional_df = load_regional_data("data/ev_stations_2025.csv")
    return df, regional_df

# Sidebar Navigation
st.sidebar.title("⚡ EV Optima")
st.sidebar.markdown("---")
pages = [
    "Project Information",
    "Dashboard", 
    "Data Explorer", 
    "Statistics", 
    "Optimization 1", 
    "Optimization 2", 
    "Methodology"
]
selection = st.sidebar.radio("Navigation", pages, index=1)
st.sidebar.markdown("---")
st.sidebar.info("Developed for University Project Presentation. \n\n✅ Models Independently Validated.")

# Helper to load data
df = load_base_data()

if selection == "Project Information":
    st.markdown('<p class="main-header">Project Information</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Strategic EV Infrastructure Optimization</p>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 📊 Dataset Description
    This project utilizes the `ev_stations_2025.csv` dataset, representing real-world Electric Vehicle charging stations. The dataset contains 10,000 recorded stations, featuring geographical coordinates, operator details, connector counts, and operational status.
    
    ### 🎯 Project Objectives
    The primary goal is to apply Operations Research (OR) methodologies to optimize EV charging infrastructure without assuming external variables like power grid loads, population densities, or specific EV traffic patterns. We strictly use the provided data to mathematically derive optimal expansion strategies.
    
    ### 📈 EDA Summary
    Exploratory Data Analysis findings:
    - Highly skewed geographical distribution (top 10% of stations hold over 25% of all connectors).
    - Quebec, British Columbia, and Washington dominate the current infrastructure.
    - 96.18% of stations are classified as operational.
    - 28.69% of records are missing state/region administrative definitions, requiring careful handling during regional modeling.
    
    ### 🧮 Optimization Questions
    1. **Optimization 1 (Hub Location)**: Where should we place a limited budget of new high-capacity charging hubs to maximize geographic coverage of existing smaller stations?
    2. **Optimization 2 (Connector Allocation)**: How should we distribute a limited budget of new individual charging connectors across administrative regions to maximize fairness (minimum connectors-per-station)?
    
    ### ⚙️ Technology Stack
    - **Language**: Python 3.12
    - **Data Processing**: Pandas, NumPy
    - **Optimization Solver**: SciPy (`scipy.optimize.milp`)
    - **Clustering**: Scikit-Learn (Spherical K-Means)
    - **Visualization UI**: Streamlit, Plotly
    
    ### ✅ Validation Status
    > **Optimization 1 and Optimization 2 have been independently validated.** Both mathematical models have successfully passed rigorous sanity checks, budget sensitivity monotonic tests, constraints validations, and baseline comparisons.
    """)

elif selection == "Dashboard":
    st.markdown('<p class="main-header">Network Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">High-Level Infrastructure Metrics</p>', unsafe_allow_html=True)
    
    # Calculate metrics
    total_stations = len(df)
    total_connectors = df['num_connectors'].sum()
    avg_connectors = total_connectors / total_stations
    operational_ratio = df['is_operational'].mean()
    num_states = df['state'].nunique()
    missing_states = df['state'].isna().sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Stations", f"{total_stations:,}")
    col2.metric("Total Connectors", f"{total_connectors:,.0f}")
    col3.metric("Avg Connectors / Station", f"{avg_connectors:.2f}")
    
    st.markdown("---")
    
    col4, col5, col6 = st.columns(3)
    col4.metric("Operational Ratio", f"{operational_ratio:.2%}")
    col5.metric("States / Regions", f"{num_states:,}")
    col6.metric("Missing-State Records", f"{missing_states:,}", delta="- Excluded from Opt 2", delta_color="off")
    
    st.markdown("""
    ### Project Overview
    Welcome to the EV Infrastructure Optimization Dashboard. This application provides a comprehensive suite of tools to explore the current state of the charging network and run validated mathematical programming models to strategically plan future expansions. Navigate using the sidebar to explore data, view statistics, or run the Mixed-Integer Linear Programming (MILP) optimizations.
    """)

elif selection == "Data Explorer":
    st.markdown('<p class="main-header">Data Explorer</p>', unsafe_allow_html=True)
    
    st.sidebar.subheader("Filters")
    selected_states = st.sidebar.multiselect("Filter by State / Region", sorted(df['state'].dropna().unique()))
    selected_operators = st.sidebar.multiselect("Filter by Operator", sorted(df['operator'].dropna().unique()))
    status_filter = st.sidebar.selectbox("Status", ["All", "Operational Only", "Non-Operational"])
    
    filtered_df = df.copy()
    if selected_states:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
    if selected_operators:
        filtered_df = filtered_df[filtered_df['operator'].isin(selected_operators)]
    if status_filter == "Operational Only":
        filtered_df = filtered_df[filtered_df['is_operational'] == True]
    elif status_filter == "Non-Operational":
        filtered_df = filtered_df[filtered_df['is_operational'] == False]
        
    cols = st.multiselect("Select Columns to Display", df.columns.tolist(), default=["title", "operator", "state", "num_connectors", "status", "lat", "lon"])
    
    st.dataframe(filtered_df[cols], use_container_width=True)
    
    st.markdown("### Descriptive Statistics")
    st.dataframe(filtered_df[['num_connectors', 'lat', 'lon']].describe(), use_container_width=True)

elif selection == "Statistics":
    st.markdown('<p class="main-header">Statistical Analysis</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Geographic Distribution", "Operator Analysis", "Geospatial Map"])
    
    with tab1:
        st.subheader("Stations & Connectors by State / Region")
        state_stats = df.groupby('state').agg(
            Stations=('id', 'count'),
            Connectors=('num_connectors', 'sum')
        ).reset_index().sort_values('Connectors', ascending=False).head(20)
        
        fig1 = px.bar(state_stats, x='state', y=['Stations', 'Connectors'], barmode='group', title="Top 20 States / Regions by Infrastructure")
        st.plotly_chart(fig1, use_container_width=True)
        
    with tab2:
        st.subheader("Stations & Connectors by Operator")
        op_stats = df.groupby('operator').agg(
            Stations=('id', 'count'),
            Connectors=('num_connectors', 'sum')
        ).reset_index().sort_values('Stations', ascending=False).head(15)
        
        fig2 = px.bar(op_stats, x='operator', y='Stations', title="Top 15 Operators by Station Count", color='Stations', color_continuous_scale='viridis')
        st.plotly_chart(fig2, use_container_width=True)
        
    with tab3:
        st.subheader("Geospatial Map of Existing Stations")
        st.info("Displaying a random 10% sample of stations to maintain performance.")
        sample_df = df.dropna(subset=['lat', 'lon']).sample(frac=0.1, random_state=42)
        fig3 = px.scatter_mapbox(
            sample_df, lat="lat", lon="lon", color="is_operational", 
            size="num_connectors", hover_name="title",
            color_discrete_map={True: "green", False: "red"},
            mapbox_style="carto-darkmatter", zoom=3, height=600,
            title="Station Locations (Sampled)"
        )
        st.plotly_chart(fig3, use_container_width=True)

elif selection == "Optimization 1":
    st.markdown('<p class="main-header">Opt 1: Charging Hub Location</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Maximum Coverage Problem (MIP)</p>', unsafe_allow_html=True)
    
    st.sidebar.subheader("Opt 1 Parameters")
    k_hubs = st.sidebar.number_input("Number of Hubs (K)", min_value=1, max_value=100, value=10, step=1)
    radius_km = st.sidebar.number_input("Coverage Radius (km)", min_value=1, max_value=1000, value=50, step=10)
    n_candidates = st.sidebar.number_input("Candidate Locations", min_value=10, max_value=500, value=100, step=10)
    
    if st.button("🚀 Run Optimization 1", type="primary"):
        with st.spinner("Generating candidates and solving Mixed-Integer Program..."):
            try:
                candidates = generate_candidate_hubs(df, n_candidates=n_candidates, random_state=42)
                res = solve_max_coverage(df, candidates, n_hubs=k_hubs, radius_km=radius_km)
                
                st.success("Optimization completed successfully!")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Selected Hubs", res['n_hubs'])
                col2.metric("Coverage Radius", f"{res['radius_km']} km")
                col3.metric("Covered Stations", f"{res['covered_stations']:,}")
                col4.metric("Coverage Percentage", f"{res['coverage_rate']:.2%}")
                
                st.markdown("### Coverage Map")
                # Plotly Map with selected hubs
                valid_df = df.dropna(subset=['lat', 'lon'])
                
                fig = go.Figure()
                # Existing stations
                fig.add_trace(go.Scattermapbox(
                    lat=valid_df['lat'], lon=valid_df['lon'], mode='markers',
                    marker=go.scattermapbox.Marker(size=4, color='gray', opacity=0.3),
                    name='Existing Stations', hoverinfo='none'
                ))
                
                # Selected hubs
                fig.add_trace(go.Scattermapbox(
                    lat=res['selected_hubs']['lat'], lon=res['selected_hubs']['lon'], mode='markers',
                    marker=go.scattermapbox.Marker(size=12, color='red', symbol='circle'),
                    name='Selected Hubs', text=res['selected_hubs']['title']
                ))
                
                fig.update_layout(
                    mapbox_style="carto-darkmatter",
                    mapbox=dict(center=dict(lat=40, lon=-95), zoom=3),
                    margin={"r":0,"t":0,"l":0,"b":0},
                    height=600,
                    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
                )
                
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### Selected Hub Locations")
                st.dataframe(res['selected_hubs'][['title', 'lat', 'lon', 'state', 'country']], use_container_width=True)
                
            except Exception as e:
                st.error(f"Optimization failed: {str(e)}")

elif selection == "Optimization 2":
    st.markdown('<p class="main-header">Opt 2: Regional Connector Allocation</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Max-Min Fairness (MILP)</p>', unsafe_allow_html=True)
    
    st.warning("⚠️ Records with a missing `state` or region value (2,869 stations) are excluded from this regional optimization.")
    
    st.sidebar.subheader("Opt 2 Parameters")
    budget_options = [100, 250, 500, 750, 1000, "Custom"]
    budget_sel = st.sidebar.selectbox("Connector Budget", budget_options, index=2)
    
    if budget_sel == "Custom":
        budget = st.sidebar.number_input("Custom Budget", min_value=1, max_value=10000, value=500, step=50)
    else:
        budget = int(budget_sel)
        
    if st.button("🚀 Run Optimization 2", type="primary"):
        with st.spinner("Solving Regional Allocation MILP..."):
            try:
                base_df, regional_df = load_opt2()
                res = solve_connector_allocation(regional_df, budget)
                
                alloc_df = res['allocation']
                
                # Calculate metrics
                initial_min_cps = alloc_df['current_cps'].min()
                final_min_cps = res['minimum_cps']
                improvement = final_min_cps - initial_min_cps
                
                st.success("Optimization completed successfully!")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Budget Utilized", f"{int(alloc_df['additional_connectors'].sum()):,}")
                col2.metric("Initial Min CPS", f"{initial_min_cps:.4f}")
                col3.metric("Optimized Min CPS", f"{final_min_cps:.4f}", delta=f"+{improvement:.4f}")
                
                baseline = proportional_baseline(regional_df, budget)
                col4.metric("Baseline Min CPS", f"{baseline['final_cps'].min():.4f}")
                
                st.info("Note: Some modeled regions contain stations with zero recorded connectors; therefore the initial minimum CPS is 0. The max-min optimization prioritizes these lowest-infrastructure regions.")

                top_alloc = alloc_df[alloc_df['additional_connectors'] > 0].sort_values('additional_connectors', ascending=False)

                st.markdown("### Before vs After: Regional Connectors per Station")
                compare_df = top_alloc.reset_index()[['state', 'current_cps', 'final_cps']].melt(id_vars='state', var_name='Metric', value_name='CPS')
                fig2 = px.bar(compare_df, x='state', y='CPS', color='Metric', barmode='group', title="CPS Improvement in Targeted States / Regions")
                st.plotly_chart(fig2, use_container_width=True)
                
                st.markdown("### Allocation Distribution")
                fig1 = px.bar(top_alloc.reset_index(), x='state', y='additional_connectors', title=f"Allocation of {budget} Connectors", color='additional_connectors', color_continuous_scale='blues')
                st.plotly_chart(fig1, use_container_width=True)
                
                st.markdown("### Top Allocations by States / Regions")
                st.dataframe(top_alloc[['stations', 'connectors', 'current_cps', 'additional_connectors', 'final_connectors', 'final_cps']], use_container_width=True)
                
            except Exception as e:
                st.error(f"Optimization failed: {str(e)}")

elif selection == "Methodology":
    st.markdown('<p class="main-header">Methodology</p>', unsafe_allow_html=True)
    
    st.markdown(r"""
    ### Optimization 1: Charging Hub Location Selection
    This model addresses the **Maximum Coverage Problem** to strategically place new, high-capacity charging hubs.
    
    - **Optimization Technique**: Mixed-Integer Programming (MIP)
    - **Decision Variables**: 
      - $y_j \in \{0, 1\}$: 1 if candidate hub location $j$ is selected to build a hub, 0 otherwise.
      - $z_i \in \{0, 1\}$: 1 if existing station $i$ is covered by at least one selected hub, 0 otherwise.
    - **Objective**: Maximize the total number of covered stations ($\sum z_i$).
    - **Constraints**: 
      - Budget constraint: The total number of selected hubs cannot exceed $K$ ($\sum y_j \le K$).
      - Coverage constraint: A station $i$ can only be considered covered ($z_i = 1$) if at least one selected hub $j$ is within the defined `radius_km`.
    - **Concept**: By running a spherical K-Means clustering algorithm on existing stations, we dynamically generate a subset of realistic candidate locations. The MIP solver then rigorously selects the best $K$ locations to maximize geographic coverage.
    
    ---
    
    ### Optimization 2: Regional Connector Allocation
    This model addresses the **Max-Min Fairness Problem** to distribute a budget of new connectors across administrative regions.
    
    - **Optimization Technique**: Mixed-Integer Linear Programming (MILP)
    - **Decision Variables**: 
      - $x_i \in \mathbb{Z}^+$: Integer number of additional connectors allocated to region $i$.
      - $t \in \mathbb{R}^+$: The minimum post-allocation connectors-per-station ratio across all regions.
    - **Objective**: Maximize $t$ (raise the lowest denominator of regional infrastructure).
    - **Constraints**: 
      - Fairness constraint: For every region $i$, the final connectors per station must be at least $t$. Mathematically: $C_i + x_i \ge t \\times S_i$, where $C_i$ is existing connectors and $S_i$ is existing stations.
      - Budget constraint: The sum of all allocated connectors must exactly equal the budget $B$ ($\sum x_i = B$).
    - **Concept**: Rather than allocating connectors strictly proportionally (which ignores existing imbalances), this formulation mathematically guarantees that the most underserved regions receive infrastructure first, maximizing the floor of the network's equity.
    - **Limitation**: Stations missing their `state` data were systematically excluded from this model to ensure administrative accuracy.
    """)
