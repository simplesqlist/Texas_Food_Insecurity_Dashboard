import streamlit as st 
from database.queries import get_county_metrics

st.set_page_config( 
    page_title="Texas Food Insecurity Dashboard",
    page_icon="📊",
    layout = "wide"
)

# Dashboard Title

st.title("Texas Food Insecurity Dashboard")
st.write("Analyze county-level food insecurity risk across Texas.")


# Load Data 

metrics = get_county_metrics()

# Sidebar Filters 

st.sidebar.subheader("Dashboard Filters")

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

# Apply Filters 

filtered_metrics = metrics[
    metrics["risk_level"].isin(selected_risk_levels)
].copy()

# Prevent errors if the user removes every selection 

if filtered_metrics.empty: 
    st.warning("Select at least one risk level to display dashboard results. ")
    st.stop()


# Calculate Dashboard Values 

total_counties = len(filtered_metrics) 
average_food_risk = round(filtered_metrics["food_risk_score"].mean(), 2)

# The SQL query already sorts food_risk_score from highest to lowest 
highest_county = filtered_metrics.iloc[0]["county_name"]
lowest_county = filtered_metrics.iloc[-1]["county_name"]

# KPI Cards 

col1, col2, col3, col4 = st.columns(4)

with col1: 
    st.metric(
        "Total Counties", 
        total_counties 
    )
with col2: 
    st.metric(
        "Average Food Risk", 
        average_food_risk 
    )
with col3: 
    st.metric(
        "Highest Risk County",
        highest_county
    )
with col4: 
    st.metric(
        "Lowest Risk County",
        lowest_county
    )



# Top 10 Highest Risk Counties 

st.subheader("Top 10 Highest Risk Counties")
top10 = filtered_metrics.head(10) 
st.bar_chart(
    top10.set_index("county_name")["food_risk_score"]
)

# Risk-Level distribution 

st.subheader("Risk Level Distribution")
risk_counts = ( 
    filtered_metrics["risk_level"]
    .value_counts()
    .reindex(available_risk_levels, fill_value = 0)
)

st.bar_chart(risk_counts)


# County Table

st.subheader("County Food Risk Data")
st.dataframe(
    filtered_metrics, 
    use_container_width = True, 
    hide_index = True
)


