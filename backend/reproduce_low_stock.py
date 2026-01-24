import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from nl_sql import generate_sql

queries = [
    "Which products are low on stock?",
    "show me low stock items",
    "low stock"
]

print("--- STARTING LOW STOCK REPRODUCTION ---")
for q in queries:
    print(f"\nQuery: {q}")
    sql = generate_sql(q)
    print(f"Generated SQL: {sql}")
    if not sql:
        print("❌ FAILED to generate SQL")
    else:
        print("✅ SQL Generated")
print("\n--- FINISHED REPRODUCTION ---")
