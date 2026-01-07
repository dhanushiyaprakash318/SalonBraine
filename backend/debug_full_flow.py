import os
import sys
import json
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from nl_sql import generate_sql, generate_conversational_response, validate_sql_safety
from sql_runner import run_sql_query
from analysis_service import generate_analysis

def test_full_query(question):
    print(f"\n--- Testing Question: {question} ---")
    
    # Step 1: SQL Gen
    sql = generate_sql(question)
    print(f"SQL Generated: {sql}")
    
    if validate_sql_safety(sql):
        try:
            # Step 2: DB Run
            data = run_sql_query(sql)
            print(f"Data returned: {len(data)} rows")
            
            # Step 3: Analysis
            analysis = generate_analysis(question, data)
            print(f"Analyst Output: {analysis}")
        except Exception as e:
            print(f"DB Error: {e}")
            conv = generate_conversational_response(question, str(e))
            print(f"Conversational Fallback: {conv}")
    else:
        print("SQL Generation failed or unsafe.")
        conv = generate_conversational_response(question, sql)
        print(f"Conversational Fallback: {conv}")

questions = [
    "How many customers do we have?",
    "Show top 5 services by revenue",
    "Which products are low on stock?"
]

for q in questions:
    test_full_query(q)
