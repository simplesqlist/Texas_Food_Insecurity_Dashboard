
from pathlib import Path

import pandas as pd


def get_county_metrics() -> pd.DataFrame:
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "dashboard_data.csv"

    return pd.read_csv(csv_path)


def get_dashboard_kpis(): 
    metrics = get_county_metrics()

    return pd.DataFrame({
        "total_counties": [len(metrics)],
        "average_food_risk": [
            round(metrics["food_risk_score"].mean(), 2)
        ],
        "highest_score": [
            round(metrics["food_risk_score"].max(), 2)
        ],
        "lowest_score": [
            round(metrics["food_risk_score"].min(), 2)
        ]
    })

