from database.queries import get_county_metrics 
from ai.ai_service import answer_question 

metrics = get_county_metrics() 

test_questions = [ 
    "Show me the top 5 highest risk counties", 
    "Tell me about Harris County", 
    "Compare Harris County and Hidalgo County", 
    "Why is Dimmit County high risk?", 
    "Which counties have high poverty and low SNAP?",
    "Show me the 5 counties with the highest poverty",
    "Which 5 counties have the highest SNAP?",
    "Show the top 5 counties with the highest unemployment",
    "Which 5 counties have the lowest income?",
]

for question in test_questions: 
    print("\nQUESTION:")
    print(question)

    result = answer_question( 
        question, 
        metrics
    )

    print("\nANSWER:")
    print(result["answer"])

    print("-" * 60)