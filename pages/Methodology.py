import streamlit as st 

st.set_page_config(
    page_title = "methodology", 
    page_icon = "📋",
    layout = "wide"
)

# Page title 

st.title("📋 Methodology")

st.write( 
    "This page explains the data, calculations, and assumptions used "
    "to estimate food insecurity risk across Texas counties."
)

# Project objective 

st.header("Project Objective")

st.write(
    "The goal of this project is to help nonprofit organizations identify " 
    "Texas counties can be compared and prioritized."
)

# Data source 

st.header("Data Source")

st.write( 
    "County level data was downloaded from Data Commons, which brings "
    "together public data from sources such as the U.S. Census Bureau, "
    "the Bureau of Labor Statistics, and the CDC."
)

st.write("The analysis includes the following variables:")

st.markdown(
    """
    - **Household Median Income:** Typical household income in each county.
    - **Poverty Count:** Number of residents living below the poverty level.
    - **SNAP RATE:** Percentage of adults receiving SNAP or food stamp assistance. 
    - **Unemployment Rate:** Percentage of the labor force that is unemployed.
    - **Total Population:** Number of residents in each county
    """
)

# Data years 

st.header("Data Year Limitation")

st.write(
    "The variable represent the latest available county level values, "
    "but they do not all come from the same year. "
)

st.markdown(
    """
    - Household income: 2024
    - Poverty count: 2024
    - SNAP rate: 2022
    - Population: 2025
    - Unemployment: April 2026
    """
)

st.info( 
    "Because public datasets are updated on different schedules, the score "
    "should be interpreted as a current county risk snapshot rather than a "
    "single year causal analysis."
)

# Poverty rate 

st.header("Poverty Rate Calculation")

st.write( 
    "The source file included the number of residents living in poverty. "
    "A rate was calculated so counties of different sizes could be compared fairly."
)

st.code(
    """

poverty_rate = (poverty_count / population) * 100
""",
    language = "text"
)

st.write(
    "For example, 10,000 residents in poverty means something different in "
    "a county of 50,000 people than in a county of one million people."
)

# Normalization 

st.header("Min-Max Normalization")

st.write( 
    "The four risk indicators use different units. Income is measured in dollars, "
    "while poverty, SNAP, and unemployment are measured as percentages."
)

st.write( 
    "Each indicator was converted to a common scale from 0 to 100 using "
    "min-max normalization."
)

st.code( 
    """
normalized_value = 
(value - minimum_value)
/ 
(maximum_value - minimum_value)
* 100
""", 
    language = "text"
)

st.markdown(
    """
    - **0** represents the lowest relative risk among Texas counties.
    - **100** represents the highest relative risk among Texas counties.
    """
)

# Income reversal 

st.header("Income Risk Reversal")

st.write(
    "Income works in the opposite direction from the other indicators."
)

st.markdown( 
    """
    - Higher poverty means higher risk. 
    - Higher SNAP participation means higher observed need. 
    - Higher unemployment means higher risk. 
    - Higher household income means lower risk.
    """
)

st.write( 
    "The normalized income value was therefore reversed so all four components"
    "point in the same direction."
)

st.code( 
    """
normalized_income_risk = 100 - normalized_income
""", 
    language = "text"
)

st.write( 
    "After this reversal, a higher value always means greater risk for every component."
)

# Food RiskScore 

st.header("Food Risk Score")

st.write( 
    "The final Food Risk Score is the average of the four normalized components."
)

st.code( 
    """
food_risk_score = 
( 
    normalized_poverty 
    + normalized_snap 
    + normalized_unemployment 
    + normalized_income_risk
) / 4
""", 
    language = "text"
)

st.write( 
    "Each component receives an equal 25% weight."
)

st.write( 
    "Equal weighting was selected because the project does not have validated "
    "evidence showing that one factor should receive more importance than another. "
    "This makes the scoring method simple, transparent, and easy to explain."
)

# Risk classification 

st.header("Risk Quartiles and Levels")

st.write( 
    "Counties were ordered by Food Risk Score and divided into four approximately "
    "equal groups using NITLE(4)."
)

risk_table = { 
    "Risk Quartile": [1, 2, 3, 4],
    "Risk Level": [ 
        "Low Risk", 
        "Moderate Risk", 
        "High Risk", 
        "Severe Risk"
    ], 
    "Interpretation": [ 
        "Lowest 25% of county scores", 
        "Second lowest 25%", 
        "Second highest 25%"
        "Highest 25% of county scores"

    ]
}

st.table(risk_table)

st.write( 
    "The risk levels are relative rankings among Texas counties. "
    "They are designed for prioritization and should not be treated as medical, "
    "legal, or official government classifications."
)

# Interpretation Limitations 

st.header("Interpretation and Limitations")

st.markdown( 
    """
    - The food Risk Score is a decision support tool, not a direct measurement 
    of household food insecurity. 
    - SNAP data covers adults age 18 and older, so it does not fully represent children receiving assitance.
    - Different variables come from different years. 
    - Correlation between indicators does not prove that one variable causes another. 
    - The score identifies relative risk among counties and should be combined with local knowledge before funding decisions are made
    """
)

# Recommended use 

st.header("Recommended Use")

st.write( 
    "Nonprofits can use the dashboard to identify counties for additional review, "
    "compare local economic conditions, and support decisions about outreach, "
    "food distribution, and resource allocation."
)

st.warning( 
    "The score should guide investigation and prioritization, not replace "
    "community input or program level needs assesments."
)