
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.getcwd())
load_dotenv()

try:
    from nl_sql import generate_sql
    print("Testing SQL Generation for: 'Show revenue trend for last 6 months'")
    sql = generate_sql("Show revenue trend for last 6 months")
    print(f"Generated SQL: {sql}")
    
    if sql and "SELECT" in sql:
        print("SUCCESS: Valid SQL generated.")
    else:
        print("FAILURE: No valid SQL generated.")
        
except Exception as e:
    print(f"ERROR: {e}")
