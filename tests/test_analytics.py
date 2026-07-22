from database.queries import get_county_metrics
from analytics.county_analysis import ( 
    get_highest_risk_counties, 
    get_county_summary,
    compare_counties,
    get_high_poverty_low_snap,
    get_largest_risk_driver
)

metrics = get_county_metrics()

print("\nTOP 5 HIGHEST RISK COUNTIES")
print( 
    get_highest_risk_counties(
        metrics, 
        limit = 5
    )
)

print("\nHARRIS COUNTY SUMMARY")
print(
    get_county_summary(
        metrics, 
        "Harris County"
    )
)

print("\nCOUNTY COMPARISON")
print( 
    compare_counties(
        metrics, 
        "Harris County", 
        "Hidalgo County"
    )
)

print("\nHIGH POVERTY AND LOW SNAP COUNTIES")
print( 
    get_high_poverty_low_snap(metrics)
)

print("\nLARGEST RISK DRIVER")
print( 
    get_largest_risk_driver( 
        metrics, 
    )
)