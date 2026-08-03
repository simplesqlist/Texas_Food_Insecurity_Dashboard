import pandas as pd 

def get_highest_risk_counties(
        metrics: pd.DataFrame, 
        limit: int = 10 
) -> pd.DataFrame: 
    """
    Return the highest risk counties.

    Parmaeters: 
        metrics: County level dashboard DataFrame. 
        limit: Number of counties to return.

    Returns: 
        A DataFrame ordered from highest to lowest Food Risk Score.
    
    """

    if limit <= 0: 
        raise ValueError("limit must be greater than zero.")
    
    required_columns = { 
        "county_name", 
        "food_risk_score", 
        "risk_level"
    }

    missing_columns = required_columns - set(metrics.columns)

    if missing_columns: 
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )
    return ( 
        metrics[
            [
                "county_name", 
                "food_risk_score", 
                "risk_level"
            ]
        ]
        .sort_values(
            by = "food_risk_score", 
            ascending = False 
        )
        .head(limit)
        .reset_index(drop = True)
    )

def get_county_summary(
        metrics: pd.DataFrame, 
        county_name: str 
) -> pd.DataFrame: 
    """
    Return the full profile for one county. 

    Parameters: 
        metrics: County level dashboard DataFrame. 
        county_name: County selected by the user. 

    Returns: 
        A one-row DataFrame containing the county profile.
    """

    if not county_name or not county_name.strip(): 
        raise ValueError("county_name cannot be empty.")
    
    matching_county = metrics[
        metrics["county_name"].str.lower()
        == county_name.strip().lower()
    ].copy()

    if matching_county.empty: 
        raise ValueError(
            f"No county named '{county_name}' was found."
        )
    
    return matching_county.reset_index(drop = True)

def compare_counties(
        metrics: pd.DataFrame, 
        first_county: str, 
        second_county: str
) -> pd.DataFrame:
    """
    Compare two counties using the dashboard's core metrics. 

    Parameters: 
        metrics: County level dashboard DataFrame.
        first_county: First county name. 
        second_county: Second county name. 

    Returns: 
        A two-row comparison DataFrame.
    """

    selected_counties = {
        first_county.strip().lower(), 
        second_county.strip().lower()
    }

    comparison = metrics[ 
        metrics["county_name"]
        .str.lower()
        .isin(selected_counties)
    ].copy()

    if len(comparison) != 2: 
        raise ValueError( 
            "Both county names must exist and must be different."
        )
    
    comparison_columns = [ 
        "county_name", 
        "food_risk_score", 
        "risk_level", 
        "poverty_rate", 
        "snap_rate", 
        "unemployment_rate", 
        "household_median_income"
    ]

    return ( 
        comparison[comparison_columns]
        .sort_values( 
            by = "food_risk_score",
            ascending = False 
        )
        .reset_index(drop = True)
    )

def get_high_poverty_low_snap(
        metrics: pd.DataFrame 
) -> pd.DataFrame: 
    """
    Return counties in the highest poverty quartile and 
    the lower half of SNAP participation. 

    Parameters: 
        metrics: County level dashboard DataFrame.

    Returns: 
        A DataFrame of counties that may warrant additional 
        SNAP outreach or program access review. 
    """

    required_columns = { 
        "county_name", 
        "poverty_rate", 
        "snap_rate", 
        "food_risk_score", 
        "risk_level"
    }

    missing_columns = required_columns - set(metrics.columns)

    if missing_columns: 
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )
    
    ranked_metrics = metrics.copy()

    ranked_metrics["poverty_quartile"] = pd.qcut(
        ranked_metrics["poverty_rate"],
        q = 4, 
        labels = [1, 2, 3, 4]
    )

    ranked_metrics["snap_quartile"] = pd.qcut( 
        ranked_metrics["snap_rate"],
        q = 4, 
        labels = [1, 2, 3, 4]
    )
    
    result = ranked_metrics[ 
        (ranked_metrics["poverty_quartile"] == 4)
        & (ranked_metrics["snap_quartile"] <= 2)
    ].copy()

    result_columns = [ 
        "county_name", 
        "poverty_rate", 
        "snap_rate", 
        "food_risk_score", 
        "risk_level"
    ]

    return ( 
        result[result_columns]
        .sort_values(
            by = ["poverty_rate", "snap_rate"],
            ascending = [False, True]
        )
        .reset_index(drop = True)

    )

def get_largest_risk_driver(
        metrics: pd.DataFrame, 
        county_name: str 
) -> dict: 
    """
    Identify the largest normalized risk component for one county. 

    Parameters: 
         metrics: County level dashboard DataFrame. 
         county_name: County selected by the user. 

    Returns: 
        A dictionary containing the county name, largest risk factor, 
        component score, Food Risk Score, and risk level.
    """

    required_columns = { 
        "county_name", 
        "food_risk_score", 
        "risk_level", 
        "normalized_poverty", 
        "normalized_snap",
        "normalized_unemployment", 
        "normalized_income_risk"
    }

    missing_columns = required_columns - set(metrics.columns)

    if missing_columns: 
        raise ValueError( 
            f"Missing required columns: {sorted(missing_columns)}"
        )
    
    if not county_name or not county_name.strip(): 
        raise ValueError("county_name cannot be empty.")
    
    matching_county = metrics[ 
        metrics["county_name"].str.lower()
        == county_name.strip().lower()
    ]

    if matching_county.empty: 
        raise ValueError( 
            f"No county named '{county_name}' was found."
        )
    
    county = matching_county.iloc[0]

    risk_components = {
        "Poverty": county["normalized_poverty"],
        "SNAP Participation": county["normalized_snap"],
        "Unemployment": county["normalized_unemployment"],
        "Income Risk": county["normalized_income_risk"]
    }

    largest_factor = max(
        risk_components, 
        key = risk_components.get 
    )

    return { 
        "county_name": county["county_name"], 
        "largest_risk_factor": largest_factor, 
        "component_score": round( 
            float(risk_components[largest_factor]),
            2
        ), 
        "food_risk_score": round( 
            float(county["food_risk_score"]), 
            2
        ), 
        "risk_level": county["risk_level"]
    }

def get_highest_poverty_counties(
        metrics: pd.DataFrame, 
        limit: int = 10 
) -> pd.DataFrame:
    """
    Return counties with the highest poverty rates.

    Parameters:
        metrics: County-level dashboard DataFrame.
        limit: Number of counties to return.

    Returns:
        A DataFrame ordered from highest to lowest poverty rate.
    """

    if limit <= 0:
        raise ValueError("limit must be greater than zero.")

    required_columns = {
        "county_name",
        "poverty_rate",
        "food_risk_score",
        "risk_level"
    }

    missing_columns = required_columns - set(metrics.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    return (
        metrics[
            [
                "county_name",
                "poverty_rate",
                "food_risk_score",
                "risk_level"
            ]
        ]
        .sort_values(
            by="poverty_rate",
            ascending=False
        )
        .head(limit)
        .reset_index(drop=True)
    )


def get_highest_snap_counties(
    metrics: pd.DataFrame,
    limit: int = 10
) -> pd.DataFrame:
    """
    Return counties with the highest SNAP participation rates.

    Parameters:
        metrics: County level dashboard DataFrame.
        limit: Number of counties to return.

    Returns:
        A DataFrame ordered from highest to lowest SNAP rate.
    """

    if limit <= 0:
        raise ValueError("limit must be greater than zero.")

    required_columns = {
        "county_name",
        "snap_rate",
        "poverty_rate",
        "food_risk_score",
        "risk_level"
    }

    missing_columns = required_columns - set(metrics.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    return (
        metrics[
            [
                "county_name",
                "snap_rate",
                "poverty_rate",
                "food_risk_score",
                "risk_level"
            ]
        ]
        .sort_values(
            by="snap_rate",
            ascending=False
        )
        .head(limit)
        .reset_index(drop=True)
    )


def get_highest_unemployment_counties(
    metrics: pd.DataFrame,
    limit: int = 10
) -> pd.DataFrame:
    """
    Return counties with the highest unemployment rates.

    Parameters:
        metrics: County level dashboard DataFrame.
        limit: Number of counties to return.

    Returns:
        A DataFrame ordered from highest to lowest unemployment rate.
    """

    if limit <= 0:
        raise ValueError("limit must be greater than zero.")

    required_columns = {
        "county_name",
        "unemployment_rate",
        "poverty_rate",
        "food_risk_score",
        "risk_level"
    }

    missing_columns = required_columns - set(metrics.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    return (
        metrics[
            [
                "county_name",
                "unemployment_rate",
                "poverty_rate",
                "food_risk_score",
                "risk_level"
            ]
        ]
        .sort_values(
            by="unemployment_rate",
            ascending=False
        )
        .head(limit)
        .reset_index(drop=True)
    )


def get_lowest_income_counties(
    metrics: pd.DataFrame,
    limit: int = 10
) -> pd.DataFrame:
    """
    Return counties with the lowest household median incomes.

    Parameters:
        metrics: County level dashboard DataFrame.
        limit: Number of counties to return.

    Returns:
        A DataFrame ordered from lowest to highest household income.
    """

    if limit <= 0:
        raise ValueError("limit must be greater than zero.")

    required_columns = {
        "county_name",
        "household_median_income",
        "poverty_rate",
        "food_risk_score",
        "risk_level"
    }

    missing_columns = required_columns - set(metrics.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    return (
        metrics[
            [
                "county_name",
                "household_median_income",
                "poverty_rate",
                "food_risk_score",
                "risk_level"
            ]
        ]
        .sort_values(
            by="household_median_income",
            ascending=True
        )
        .head(limit)
        .reset_index(drop=True)
    )

def get_statewide_summary(
        metrics: pd.DataFrame
) -> dict:
    """
    Return statewide summary statistics for the dashboard.

    Parameters:
        metrics: County-level dashboard DataFrame.

    Returns:
        A dictionary containing statewide Food Risk Score statistics
        and county counts by risk level.
    """

    required_columns = {
        "county_name",
        "food_risk_score",
        "risk_level"
    }

    missing_columns = required_columns - set(metrics.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if metrics.empty:
        raise ValueError("The county metrics dataset is empty.")

    highest_county = metrics.loc[
        metrics["food_risk_score"].idxmax()
    ]

    lowest_county = metrics.loc[
        metrics["food_risk_score"].idxmin()
    ]

    risk_counts = (
        metrics["risk_level"]
        .value_counts()
        .to_dict()
    )

    return {
        "total_counties": int(len(metrics)),
        "average_food_risk_score": round(
            float(metrics["food_risk_score"].mean()),
            2
        ),
        "highest_risk_county": highest_county["county_name"],
        "highest_food_risk_score": round(
            float(highest_county["food_risk_score"]),
            2
        ),
        "lowest_risk_county": lowest_county["county_name"],
        "lowest_food_risk_score": round(
            float(lowest_county["food_risk_score"]),
            2
        ),
        "risk_level_counts": risk_counts
    }