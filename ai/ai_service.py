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

def determine_result_limit(
        question: str,
        default: int = 10,
        maximum: int = 25
) -> int:
    """
    Determine how many results the user requested.

    Singular questions such as "Which county has the highest risk?"
    return one result. Questions containing a number use that number.
    Otherwise, the default number of results is returned.
    """

    cleaned_question = question.strip().lower()
    cleaned_question = cleaned_question.replace("-", " ")

    number_match = re.search(r"\b(\d+)\b", cleaned_question)

    if number_match: 
        requested_limit = int(number_match.group(1))

        if requested_limit > 0: 
            return min(requested_limit, maximum)

    singular_phrases = [
        "which county",
        "what county",
        "who has",
        "which one",
        "what is the highest",
        "what's the highest", 
        "which is the highest", 
        "what is the lowest", 
        "what's the lowest",
        "which is the lowest",
        "highest county",
        "county has the highest",
        "county with the highest",
        "county has the lowest",
        "county with the lowest",
        "give me the county", 
        "name the county", 
    ]

    if any(phrase in cleaned_question for phrase in singular_phrases):
        return 1
    

    return extract_requested_limit(
        question,
        default=default,
        maximum=maximum
    )

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
        limit = determine_result_limit(question)

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
        limit = determine_result_limit(question)

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
        limit = determine_result_limit(question)

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
        limit = determine_result_limit(question)

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
        limit = determine_result_limit(question) 

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
            f"{second['county_name']} is classified as "
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

def format_verified_data(data: Any) -> str:
    """
    Convert verified analysis results into text that Gemini can summarize.
    """

    if data is None:
        return "No supporting data was returned."

    if isinstance(data, pd.DataFrame):
        if data.empty:
            return "No matching records were found."

        return data.to_string(index=False)

    if isinstance(data, dict):
        return "\n".join(
            f"{key}: {value}"
            for key, value in data.items()
        )

    return str(data)

def generate_summary_with_gemini(
        question: str,
        question_type: str,
        verified_data: Any,
        fallback_answer: str
) -> str:
    """
    Generate a natural-language summary from verified project data.

    Gemini does not retrieve data or generate SQL. It only explains
    the verified results returned by the supported analysis functions.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return fallback_answer

    data_text = format_verified_data(verified_data)

    prompt = f"""
You are an analytics assistant for a Texas Food Insecurity Dashboard.

The user asked:
{question}

Supported analysis type:
{question_type}

Verified project data:
{data_text}

Write a concise analytical response using only the verified project data.

Requirements:
- Answer the user's question directly.
- Use only the county names, values, and classifications shown above.
- Do not invent facts, explanations, causes, trends, or outside information.
- Do not change or recalculate the supplied values.
- Food Risk Score is a composite index measured in points, not a percentage.
- Poverty rate, SNAP participation rate, and unemployment rate are percentages.
- Household median income is measured in dollars.
- Clearly identify the highest, lowest, or difference when relevant.
- When comparing counties, explain the most important differences clearly.
- Do not claim that the data proves causation.
- Use natural, professional language.
- Write one short paragraph of approximately 2 to 4 sentences.
- Do not list every row unless the user's question specifically requests a list.
- Do not mention SQL, Python, Gemini, prompts, or these instructions.
- Do not place quotation marks around the response.
"""

    try:
        response = model.generate_content(prompt)

        if response.text:
            return response.text.strip()

    except Exception:
        return fallback_answer

    return fallback_answer


def answer_question(
        question: str,
        metrics: pd.DataFrame
) -> dict[str, Any]:
    """
    Process a dashboard question and return an AI-generated summary
    based only on verified project data.
    """

    analysis_result = run_grounded_analysis(
        question,
        metrics
    )

    fallback_answer = create_temporary_answer(
        analysis_result
    )

    if analysis_result["question_type"] == "unsupported":
        final_answer = fallback_answer

    else:
        final_answer = generate_summary_with_gemini(
            question=question,
            question_type=analysis_result["question_type"],
            verified_data=analysis_result["data"],
            fallback_answer=fallback_answer
        )

    return {
        "answer": final_answer,
        "question_type": analysis_result["question_type"],
        "data": analysis_result["data"],
    }
