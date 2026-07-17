import streamlit as st 

from database.queries import get_county_metrics 

st.set_page_config( 
    page_title = "County Rankings", 
    page_icon = "📈", 
    layout = "wide"
) 

# Page title 

st.title("📈 County Rankings")

st.write( 
    "Compare Texas counties by food risk, poverty, SNAP participation, "
    "unemployment, and household income."
)

# Load data 

metrics = get_county_metrics()

# Sidebar filters 

st.sidebar.subheader ("Ranking Filters")

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

county_search = st.sidebar.text_input( 
    "Search County", 
    placeholder = "Example: Harris"
)

minimum_risk_score = st.sidebar.slider( 
    "Minimum Food Risk Score", 
    min_value = float(metrics["food_risk_score"].min()), 
    max_value = float(metrics["food_risk_score"].max()), 
    value = float(metrics["food_risk_score"].min()),
    step = 1.0
)

# Apply filters 

filtered_rankings = metrics[
    metrics["risk_level"].isin(selected_risk_levels)
].copy()

filtered_rankings = filtered_rankings[
    filtered_rankings["food_risk_score"] >= minimum_risk_score
]

if county_search: 
    filtered_rankings = filtered_rankings[
        filtered_rankings["county_name"].str.contains( 
            county_search, 
            case = False, 
            na = False 
        )
    ]

# Handle empty results 

if filtered_rankings.empty: 
    st.warning("No counties match the selected filters.")
    st.stop()

# Ranking summary 

st.subheader("Ranking Summary")

col1, col2, col3 = st.columns(3)

with col1: 
    st.metric(
        "Counties Shown", 
        len(filtered_rankings)
    )

with col2: 
    st.metric( 
        "Highest Food Risk Score", 
        round(filtered_rankings["food_risk_score"].max(), 2)
    )

with col3: 
    st.metric( 
        "Average Food Risk Score", 
        round(filtered_rankings["food_risk_score"].mean(), 2)
    )

# Top 20 chart 

st.subheader("Top 20 Highest Risk Counties")

top20 = filtered_rankings.head(20)

st.bar_chart(  
    top20.set_index("county_name")["food_risk_score"]
)

# County ranking table 

st.subheader("County Ranking Table")

st.dataframe(
    filtered_rankings, 
    use_container_width = True, 
    hide_index = True 
)

# Download filtered results 

csv_data = filtered_rankings.to_csv(index = False).encode("utf-8")

st.download_button( 
    label ="Download Filtered County Rankings", 
    data = csv_data, 
    file_name = "texas_county_rankings.csv", 
    mime = "text/csv"
)