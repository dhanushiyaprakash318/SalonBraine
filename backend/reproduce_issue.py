import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from nl_sql import generate_sql

queries = [
    "compae this month revenue with last month",
    "compare this month revenue with last month",
    "revenue comparison this month vs last month"
]

print("--- STARTING REPRODUCTION ---")
for q in queries:
    print(f"\nQuery: {q}")
    sql = generate_sql(q)
    print(f"Generated SQL: {sql}")
    if not sql:
        print("❌ FAILED to generate SQL")
    else:
        print("✅ SQL Generated")
print("\n--- FINISHED REPRODUCTION ---")
