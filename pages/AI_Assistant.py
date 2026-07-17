import pandas as pd
import streamlit as st

from ai.ai_service import answer_question
from database.queries import get_county_metrics

st.set_page_config(
    page_title = "AI Assistant", 
    page_icon = "🤖",
    layout = "wide"
)

# Page title 

st.title("🤖 Texas Food Insecurity Assistant")

st.write(
    "Ask questions about Texas county food risk, poverty, SNAP participation, "
    "unemployment, household income, and nonprofit prioritization."
)

st.info(
    "Answers are generated from the dashboard's verified county data and "
    "supported analytics functions."
)

# Load data 

metrics = get_county_metrics()

# Supported question examples 

st.subheader("Example Questions")

st.markdown(
    """
    - Show me the top 5 highest risk counties.
    - Tell me about Harris County.
    - Compare Harris County and Hidalgo County.
    - Why is Dimmit County high risk?
    - Which counties have high poverty and low SNAP?
    - Which 5 counties have the highest poverty?
    - Which counties have the highest SNAP participation?
    - Show the counties with the highest unemployment.
    - Which counties have the lowest household income?
    """
)

#question input 

user_question = st.text_input(
    "Ask a dashboard question",
    placeholder="Example: Compare Harris County and Hidalgo County"
)

submit_question = st.button(
    "Analyze Question",
    type="primary"
)

# Process question 

if submit_question:

    if not user_question.strip():
        st.warning("Enter a question before submitting.")

    else:
        try:
            with st.spinner("Analyzing the county data..."):

                result = answer_question(
                    user_question,
                    metrics
                )

            st.subheader("Answer")

            st.write(result["answer"])

            supporting_data = result["data"]

            if isinstance(supporting_data, pd.DataFrame):

                if not supporting_data.empty:
                    st.subheader("Supporting Data")

                    st.dataframe(
                        supporting_data,
                        use_container_width=True,
                        hide_index=True
                    )

            elif isinstance(supporting_data, dict):

                st.subheader("Supporting Data")

                supporting_table = pd.DataFrame(
                    [supporting_data]
                )

                st.dataframe(
                    supporting_table,
                    use_container_width=True,
                    hide_index=True
                )

        except ValueError as error:
            st.warning(str(error))

        except Exception as error:
            st.error(
                "The assistant could not process the question. "
                "Review the question and try again."
            )

            with st.expander("Technical details"):
                st.write(str(error))