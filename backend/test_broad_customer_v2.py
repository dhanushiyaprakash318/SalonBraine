
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from nl_sql import generate_sql

def test_broad_customer_queries():
    questions = [
        "show customer raj",
        "show customer mithi",
        "List all customers",
        "How many customers do we have?",
        "Details for customer Alice"
    ]
    
    print("--- Testing Broad Customer Queries ---")
    for q in questions:
        print(f"\nQuestion: {q}")
        try:
            sql = generate_sql(q)
            print(f"SQL: {sql}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_broad_customer_queries()
