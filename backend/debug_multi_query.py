import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from nl_sql import generate_sql, extract_sql

questions = [
    "How many customers are in the database?",
    "Which products are low on stock?",
    "Which products have never been sold?",
    "Show top 5 services by revenue"
]

for q in questions:
    print(f"\nQuestion: {q}")
    sql = generate_sql(q)
    print(f"Generated SQL: {sql}")
    if "SELECT" in sql.upper():
        print("RESULT: SUCCESS")
    else:
        print("RESULT: FAILURE")
