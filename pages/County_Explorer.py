import streamlit as st 
import pandas as pd

from database.queries import get_county_metrics

st.set_page_config(
    page_title = "County Explorer",
    page_icon = "🔍",
    layout = "wide",
)

st.title("🔍 County Explorer")

st.write( 
    "Select a Texas county to review its food-risk profile and economic indicators."
)

# Load data 
metrics = get_county_metrics()

#County Explorer 

selected_county = st.selectbox(
    "Choose a county", 
    options = metrics["county_name"].tolist(), 
)

# Select the single row matching the chosen county 

county_data = metrics[ 
    metrics["county_name"] == selected_county 
].iloc[0]

# County profile 

st.subheader(f"{selected_county} Profile")

col1, col2, col3 = st.columns(3) 

with col1: 
    st.metric(
        "Food Risk Score",
        f"{county_data['food_risk_score']:.2f}",
    )
with col2: 
    st.metric( 
        "Risk Level", 
        county_data["risk_level"],
    )
with col3: 
    st.metric(
        "Household Median Income", 
        f"${county_data['household_median_income']:,.0f}",
    )

col4, col5, col6 = st.columns(3)

with col4: 
    st.metric( 
        "Poverty Rate", 
        f"{county_data['poverty_rate']:.2f}%",
    )
with col5: 
    st.metric( 
        "SNAP Rate", 
        f"{county_data['snap_rate']:.2f}%",
    )
with col6: 
    st.metric(
        "Unemployment Rate",
        f"{county_data['unemployment_rate']:.2f}%",
    )

# Risk component scores 

st.subheader("Risk Score Components")

st.write( 
    "Each component is scored from 0 to 100. "
    "A higher value represents greater relative risk among Texas counties."
)

risk_components = pd.DataFrame(
    { 
        "Risk Factor": [
            "Poverty", 
            "SNAP Participation", 
            "Unemployment", 
            "Income Risk"
        ],
        "Component Score": [
            county_data["normalized_poverty"], 
            county_data["normalized_snap"],
            county_data["normalized_unemployment"],
            county_data["normalized_income_risk"]
        ] 
    }

)

st.bar_chart( 
    risk_components.set_index( "Risk Factor") 
    ["Component Score"]
)

largest_risk_factor = risk_components.loc[
    risk_components["Component Score"].idxmax()
]

st.info(
    f"The largest relative risk factor for {selected_county} is "
    f"{largest_risk_factor['Risk Factor']}"
    f"with a component score of "
    f"{largest_risk_factor['Component Score']:.2f}."
)