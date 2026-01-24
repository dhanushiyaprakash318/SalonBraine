import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from nl_sql import generate_sql
from sql_runner import run_sql_query
from database import get_db_connection

def inspect_schema():
    print("\n--- SCHEMA INSPECTION ---")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DESCRIBE master_inventory")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Schema Error: {e}")

def test_execution():
    print("\n--- EXECUTION TEST ---")
    question = "Which products are low on stock?"
    sql = generate_sql(question)
    print(f"Generated SQL: {sql}")
    
    if not sql:
        print("No SQL generated.")
        return

    try:
        print("Executing SQL...")
        data = run_sql_query(sql)
        print(f"Success! Rows returned: {len(data)}")
        print(data[:5])
    except Exception as e:
        print(f"❌ EXECUTION FAILED: {e}")

if __name__ == "__main__":
    inspect_schema()
    test_execution()
