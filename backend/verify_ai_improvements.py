import sys
import os
import json

# Add current directory to path so we can import local modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from nl_sql import generate_sql, generate_conversational_response
from analysis_service import generate_analysis

def test_comparison_generation():
    print("\n--- Testing Comparison SQL Generation ---")
    question = "compare last month revenue with this month and total revenue and last year revenue"
    sql = generate_sql(question)
    print(f"Question: {question}")
    print(f"Generated SQL: {sql}")
    if "UNION ALL" in sql and "period" in sql:
        print("✅ SUCCESS: UNION ALL pattern used for comparison.")
    else:
        print("❌ FAILURE: UNION ALL pattern not found.")

def test_fallback_conversational():
    print("\n--- Testing Conversational Fallback ---")
    question = "What is the best way to cut hair?"
    response = generate_conversational_response(question)
    print(f"Question: {question}")
    print(f"Response: {response}")
    if "Answer not found" in response or "query" in response.lower():
         print("✅ SUCCESS: Fallback message contains 'Answer not found' or similar context.")
    else:
         print("⚠️ NOTICE: Response might be direct, checking if it suggested related topics.")

def test_empty_analysis_fallback():
    print("\n--- Testing Empty Data Analysis Fallback ---")
    question = "Show me revenue for the year 1900"
    data = []
    analysis = generate_analysis(question, data)
    print(f"Question: {question}")
    print(f"Analysis: {analysis}")
    if "Answer not found" in analysis and "revenue" in analysis.lower():
        print("✅ SUCCESS: Context-aware 'Answer not found' message generated.")
    else:
        print("❌ FAILURE: Expected context-aware fallback.")

if __name__ == "__main__":
    test_comparison_generation()
    test_fallback_conversational()
    test_empty_analysis_fallback()
