import re 
from typing import Any 

import os

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")


import pandas as pd 

from analytics.county_analysis import(
    compare_counties, 
    get_county_summary, 
    get_high_poverty_low_snap,
    get_highest_poverty_counties,  
    get_highest_risk_counties,
    get_highest_snap_counties,
    get_highest_unemployment_counties,  
    get_largest_risk_driver,
    get_lowest_income_counties,
)

def find_counties_in_question( 
        question: str, 
        metrics: pd.DataFrame 
) -> list[str]: 
    """
    Find county names mentioned in the user's question. 

    The comparison is case insensitive.

    Parameters: 
        question: User's natural language question. 
        metrics: County level dashboard DataFrame. 

    Returns: 
        A list of matching county names.
    """

    question_lower = question.lower() 

    county_names = metrics["county_name"].dropna().unique() 

    matching_counties = [ 
        county_name 
        for county_name in county_names 
        if county_name.lower() in question_lower
    ]

    return matching_counties 

def identify_question_type(
        question: str, 
        metrics: pd.DataFrame 
) -> tuple[str, list[str]]: 
    """
    Classify the user's question into a supported analysis type.

    Returns: 
        A tuple containing: 
        - question type 
        - county names detected in the question
    """

    cleaned_question = question.strip().lower()

    if not cleaned_question: 
        raise ValueError("Enter a question before submitting.")
    
    counties = find_counties_in_question( 
        cleaned_question, 
        metrics 
    )

    if ( 
        any(word in cleaned_question for word in ["compare", "difference"])
        and len(counties) >= 2
    ):
        return "compare_counties", counties[:2]
    
    if ( 
        "high poverty" in cleaned_question 
        and ( 
            "low snap" in cleaned_question 
            or "low food stamp" in cleaned_question
        )
    ): 
        return "high_poverty_low_snap", counties 
    
    if any(
        phrase in cleaned_question
        for phrase in [
            "highest poverty",
            "most poverty",
            "highest poverty rate",
            "poverty counties",
        ]
    ):
            return "highest_poverty", counties
    
    if any(
        phrase in cleaned_question
        for phrase in [
            "highest snap",
            "most snap",
            "highest food stamp",
            "most food assistance",
        ]
    ):
        return "highest_snap", counties

    if any(
        phrase in cleaned_question
        for phrase in [
            "highest unemployment",
            "most unemployment",
            "worst unemployment",
            "job market problems",
        ]
    ):
        return "highest_unemployment", counties

    if any(
        phrase in cleaned_question
        for phrase in [
            "lowest income",
            "lowest household income",
            "poorest income",
            "weakest income",
        ]
    ):
        return "lowest_income", counties
    
    
    if any( 
        phrase in cleaned_question 
        for phrase in [ 
            "highest risk", 
            "top counties",
            "prioritize",
            "funding first", 
            "most assistance", 
            "most at risk",
        ]
    ): 
        return "highest_risk", counties 
    
    if ( 
        len(counties) == 1
        and any(
            phrase in cleaned_question 
            for phrase in [
                "why", 
                "driver", 
                "driving", 
                "contribute", 
                "contributor",
            ]
        )
    ): 
        return "largest_driver", counties 
    
    if len(counties) == 1:
        return "county_summary", counties 
    
    return "unsupported", counties 

def  extract_requested_limit( 
        question: str, 
        default: int = 10, 
        maximum: int = 25
) -> int: 
    """
    Extract a requested number from questions such as: 
    'Show the top 5 counties.' 

    Returns the default when no number is found.
    """

    number_match = re.search(r"\b(\d+)\b", question)

    if not number_match: 
        return default 
    
    requested_limit = int(number_match.group(1))

    if requested_limit <= 0: 
        return default 
    
    return min(requested_limit, maximum)

def run_grounded_analysis( 
        question: str, 
        metrics: pd.DataFrame 
) -> dict[str, Any]:
    """
    Run a trusted analytics function based on the user's question. 

    This function does not call an AI model. 
    It returns structured, verified data.
    """

    question_type, counties = identify_question_type( 
        question, 
        metrics 
    )

    if question_type == "highest_poverty":
        limit = extract_requested_limit(question)

        result = get_highest_poverty_counties(
            metrics,
            limit=limit
        )

        return {
            "question_type": question_type,
            "data": result,
            "message": (
                f"Showing the {len(result)} counties with the "
                "highest poverty rates."
            ),
        }

    if question_type == "highest_snap":
        limit = extract_requested_limit(question)

        result = get_highest_snap_counties(
            metrics,
            limit=limit
        )

        return {
            "question_type": question_type,
            "data": result,
            "message": (
                f"Showing the {len(result)} counties with the "
                "highest SNAP participation rates."
            ),
        }

    if question_type == "highest_unemployment":
        limit = extract_requested_limit(question)

        result = get_highest_unemployment_counties(
            metrics,
            limit=limit
        )

        return {
            "question_type": question_type,
            "data": result,
            "message": (
                f"Showing the {len(result)} counties with the "
                "highest unemployment rates."
            ),
        }

    if question_type == "lowest_income":
        limit = extract_requested_limit(question)

        result = get_lowest_income_counties(
            metrics,
            limit=limit
        )

        return {
            "question_type": question_type,
            "data": result,
            "message": (
                f"Showing the {len(result)} counties with the "
                "lowest household median incomes."
            ),
        }

    if question_type == "highest_risk": 
        limit = extract_requested_limit(question) 

        result = get_highest_risk_counties( 
            metrics, 
            limit = limit 
        )

        return { 
            "question_type": question_type, 
            "data": result, 
            "message": ( 
                f"Showing the {len(result)} highest risk counties "
                "based on Food Risk Score."
            ),
        }
    
    if question_type == "county_summary": 
        county_name = counties[0]

        result = get_county_summary(
            metrics, 
            county_name 
        )

        return { 
            "question_type": question_type, 
            "data": result,
            "message": f"County profile for {county_name}.",
        }
    
    if question_type == "compare_counties":
        first_county = counties[0]
        second_county = counties[1]

        result = compare_counties(
            metrics, 
            first_county, 
            second_county 
        )

        return { 
            "question_type": question_type, 
            "data": result, 
            "message": ( 
                f"Comparison of {first_county} "
                f"and {second_county}."
            ),
        }
    
    if question_type == "high_poverty_low_snap": 
        result = get_high_poverty_low_snap(metrics)

        return { 
            "question_type": question_type, 
            "data": result, 
            "message": ( 
                "Counties in the highest poverty quartile "
                "and lower half of SNAP participation."
            ),
        }
    
    if question_type == "largest_driver": 
        county_name = counties[0]

        result = get_largest_risk_driver(
            metrics, 
            county_name 
        )

        return { 
            "question_type": question_type, 
            "data": result, 
            "message": ( 
                f"Largest normalized risk component " 
                f"for {county_name}."
            ),
        }
    
    return { 
        "question_type": "unsupported", 
        "data": None, 
        "message": ( 
            "I could not match that question to a supported analysis. "
            "Try asking about a county profile, two-county comparison, "
            "highest Food Risk Scores, highest poverty, highest SNAP "
            "participation, highest unemployment, lowest household "
            "income, largest risk driver, or counties with high poverty "
            "and low SNAP participation."
        ),
    }

def create_temporary_answer( 
        analysis_result: dict[str, Any]
) -> str: 
    """
    Create a temporary answer based on the grounded data instead of the LLM. 

    This allows the AI Assistant workflow to be tested before 
    connecting a paid or free model provider. 
    """

    question_type = analysis_result["question_type"]
    data = analysis_result["data"]

    if question_type == "unsupported": 
        return analysis_result["message"]
    
    if question_type == "highest_risk": 
        county_list = data[ 
            ["county_name", "food_risk_score", "risk_level"]
        ].to_dict(orient = "records")

        lines = [ 
            f"{row['county_name']}: "
            f"{row['food_risk_score']:.2f} "
            f"({row['risk_level']})"
            for row in county_list 
        ]

        return ( 
            f"{analysis_result['message']}\n\n"
            + "\n".join(lines)
        )
    
    if question_type == "county_summary": 
        county = data.iloc[0]

        return ( 
            f"{county['county_name']} has a Food Risk Score of "
            f"{county['food_risk_score']:.2f}, placing it in the "
            f"{county['risk_level']} category. "
            f"Its poverty rate is "
            f"{county['poverty_rate']:.2f}%, while "
            f"{county['snap_rate']:.2f}% of adults participate in SNAP. "
            f"The county's household median income is "
            f"${county['household_median_income']:,.0f}, "
            f"and its unemployment rate is "
            f"{county['unemployment_rate']:.2f}%."
        )
    
    if question_type == "compare_counties":
        first = data.iloc[0]
        second = data.iloc[1]

        score_difference = (
        first["food_risk_score"]
        - second["food_risk_score"]
        )

        return (
            f"{first['county_name']} has a Food Risk Score of "
            f"{first['food_risk_score']:.2f}, compared with "
            f"{second['county_name']}'s score of "
            f"{second['food_risk_score']:.2f}. "
            f"The difference between the two counties is "
            f"{abs(score_difference):.2f} points. "
            f"{first['county_name']} is classified as "
            f"{first['risk_level']}, while "
            "{second['county_name']} is classified as "
            f"{second['risk_level']}."
        )

    
    if question_type == "high_poverty_low_snap":
        if data.empty: 
            return( 
                "No counties matched the definition of being in the "
                "highest poverty quartile and lower half of SNAP "
                "participation."
            )
        
        county_names = ", ".join( 
            data["county_name"].tolist()
        )

        return ( 
            f"{len(data)} counties matched the selected definition: "
            f"{county_names}. These counties may warrant additional "
            "review, but this pattern alone does not prove a SNAP "
            "access problem."
        )
    
    if question_type == "highest_poverty":
        rows = data.to_dict(orient="records")

        lines = [
            f"{row['county_name']}: "
            f"{row['poverty_rate']:.2f}% poverty "
            f"({row['risk_level']})"
            for row in rows
        ]

        return (
            f"{analysis_result['message']}\n\n"
            + "\n".join(lines)
        )
    
    if question_type == "highest_snap":
        rows = data.to_dict(orient="records")

        lines = [
            f"{row['county_name']}: "
            f"{row['snap_rate']:.2f}% SNAP participation "
            f"({row['risk_level']})"
            for row in rows
        ]

        return (
            f"{analysis_result['message']}\n\n"
            + "\n".join(lines)
        )
    
    if question_type == "highest_unemployment":
        rows = data.to_dict(orient="records")

        lines = [
            f"{row['county_name']}: "
            f"{row['unemployment_rate']:.2f}% unemployment "
            f"({row['risk_level']})"
            for row in rows
        ]

        return (
            f"{analysis_result['message']}\n\n"
            + "\n".join(lines)
        )
    
    if question_type == "lowest_income":
        rows = data.to_dict(orient="records")

        lines = [
            f"{row['county_name']}: "
            f"${row['household_median_income']:,.0f} "
            f"household median income "
            f"({row['risk_level']})"
            for row in rows
        ]

        return (
            f"{analysis_result['message']}\n\n"
            + "\n".join(lines)
        )
    
    if question_type == "largest_driver": 
        return ( 
            f"The largest normalized risk component for "
            f"{data['county_name']} is "
            f"{data['largest_risk_factor']}, with a component score "
            f"of {data['component_score']:.2f}. The county's overall "
            f"Food Risk Score is {data['food_risk_score']:.2f}, and "
            f"its risk level is {data['risk_level']}."
        )
    
    return analysis_result["message"]

def rewrite_with_gemini(
        grounded_answer: str,
        question: str
) -> str:
    """
    Rewrite a verified analytics answer using Gemini.

    Gemini is only used to improve clarity and wording.
    It must not change numbers or add unsupported facts.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return grounded_answer

    prompt = f"""

You are a senior data analyst presenting findings from a Texas food
insecurity dashboard to nonprofit leaders, program managers, and
grant decision-makers.

Rewrite the verified answer so it sounds natural, polished, and
analytical.

Requirements:
- Preserve every number exactly.
- Preserve county names and risk classifications exactly.
- Do not invent facts, causes, estimates, or external information.
- Do not claim that the data proves causation.
- Avoid awkward phrases such as "has the higher score at."
- Explain the comparison clearly when two counties are involved.
- State the practical meaning of the result only when it follows
  directly from the dashboard's scores and classifications.
- Use plain professional language.
- Keep the response to one short paragraph.
- Do not mention these instructions, the prompt, or Gemini.
- Do not place quotation marks around the response.

User question:
{question}

Verified analytical answer:
{grounded_answer}
"""

    try:
        response = model.generate_content(prompt)

        if response.text:
            return response.text.strip()

    except Exception:
        return grounded_answer

    return grounded_answer

def answer_question(
        question: str,
        metrics: pd.DataFrame
) -> dict[str, Any]:
    """
    Process a dashboard question and return a grounded,
    LLM-polished analytical response.
    """

    analysis_result = run_grounded_analysis(
        question,
        metrics
    )

    grounded_answer = create_temporary_answer(
        analysis_result
    )

    if analysis_result["question_type"] == "unsupported":
        final_answer = grounded_answer
    else:
        final_answer = rewrite_with_gemini(
            grounded_answer=grounded_answer,
            question=question
        )

    return {
        "answer": final_answer,
        "question_type": analysis_result["question_type"],
        "data": analysis_result["data"],
    }