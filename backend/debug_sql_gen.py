import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from nl_sql import generate_sql, is_sql_query, get_relevant_schema

question = "How many customers are in the database?"
print(f"Question: {question}")
print("Fetching relevant schema...")
schema = get_relevant_schema(question)
print(f"Schema length: {len(schema)}")
if not schema or schema == "No tables available":
    print("❌ ERROR: Schema is empty or unavailable!")

question = "How many customers are in the database?"
print(f"Question: {question}")
print("Generating SQL...")

sql = generate_sql(question)
with open("sql_debug.log", "w", encoding="utf-8") as f:
    f.write(sql)

print("\n--- FINAL OUTPUT ---")
print(sql)
print("--------------------")

if "SELECT" in sql.upper():
    print("✅ SUCCESS: Valid SELECT query found.")
else:
    print("❌ FAILURE: No valid SELECT query generated. Check sql_debug.log")
