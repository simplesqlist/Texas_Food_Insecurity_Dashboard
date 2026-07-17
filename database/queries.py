import pandas as pd 
from database.connection import get_connection 

def get_county_metrics(): 
    conn = get_connection() 

    query = """
    SELECT 
        c.county_name, 
        cs.food_risk_score, 
        cs.risk_level, 
        cs.poverty_rate,
        cs.normalized_poverty,
        cs.normalized_snap, 
        cs.normalized_unemployment,
        cs.normalized_income_risk,
        cm.snap_rate, 
        cm.unemployment_rate,
        cm.household_median_income 
    FROM counties c 
    JOIN county_scores cs 
        ON c.county_id = cs.county_id 
    JOIN county_metrics cm 
        ON c.county_id = cm.county_id 
    ORDER BY cs.food_risk_score DESC;
    """

    df = pd.read_sql(query, conn)
    conn.close() 
    return df 

def get_dashboard_kpis(): 
    conn = get_connection() 
    query = """ 
    SELECT 
        COUNT(*) AS total_counties, 
        ROUND(AVG(food_risk_score), 2) AS average_food_risk, 
        MAX(food_risk_score) AS highest_score, 
        MIN(food_risk_score) AS lowest_score 
    FROM county_scores; 
    """ 

    df = pd.read_sql(query, conn) 
    conn.close()
    return df 

