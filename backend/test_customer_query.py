
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from nl_sql import generate_sql

def test_customer_query():
    questions = [
        "Show details for customer John Doe",
        "How many times has Alice visited?",
        "What is the total spending of Bob?"
    ]
    
    for q in questions:
        print(f"\nQuestion: {q}")
        try:
            sql = generate_sql(q)
            print(f"SQL: {sql}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_customer_query()
