import streamlit as st 
import pandas as pd 

from database.queries import get_county_metrics 

st.set_page_config(
    page_title = "Risk Drivers", 
    page_icon = "📉", 
    layout = "wide"
)

# Page title 

st.title("📉 Risk Drivers")

st.write( 
    "Explore how household income, poverty, SNAP participation,"
    "and unemployment are related across Texas counties."
)

# Load data 

metrics = get_county_metrics()

# Sidebar filter 

st.sidebar.subheader("Risk Driver Filters")

risk_level_order = [ 
    "Low Risk", 
    "Moderate Risk", 
    "High Risk", 
    "Severe Risk"
]

available_risk_levels = [ 
    level 
    for level in risk_level_order 
    if level in metrics["risk_level"].unique()
]

selected_risk_levels = st.sidebar.multiselect( 
    "Select Risk Level", 
    options = available_risk_levels, 
    default = available_risk_levels 
)

# Apply filter 

filtered_drivers = metrics[ 
    metrics["risk_level"].isin(selected_risk_levels)
].copy()

if filtered_drivers.empty: 
    st.warning("Select at least one risk level to display results.")
    st.stop()

# Income vs Poverty 

st.subheader("Household Income vs Poverty Rate") 
st.scatter_chart( 
    filtered_drivers, 
    x = "household_median_income", 
    y = "poverty_rate"
)

st.caption( 
    "This chart tests whether counties with lower household incomes "
    "tend to have higher poverty rates."
)

# Poverty vs SNAP 

st.subheader("Poverty rate vs SNAP Rate")

st.scatter_chart( 
    filtered_drivers, 
    x = "poverty_rate",
    y = "snap_rate"
)

st.caption( 
    "This chart tests whether counties with higher poverty rates "
    "also tend to have higher SNAP participation."
)

# Unemployment vs Poverty 

st.subheader("Unemployment Rate vs Poverty Rate")

st.scatter_chart(
    filtered_drivers, 
    x = "unemployment_rate", 
    y = "poverty_rate"
)

st.caption( 
    "This chart tests whether counties with higher unemployment "
    "also tend to have higher poverty rates."
)

# Correlation table 

st.subheader("Correlation Summary")

correlation_columns = [ 
    "household_median_income", 
    "poverty_rate", 
    "snap_rate", 
    "unemployment_rate", 
    "food_risk_score"
]

correlation_matrix = ( 
    filtered_drivers[correlation_columns]
    .corr()
    .round(2)
)

st.dataframe(
    correlation_matrix, 
    use_container_width = True 
)