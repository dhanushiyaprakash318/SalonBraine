
import os
import sys
from dotenv import load_dotenv
import pandas as pd

# Add backend to path
sys.path.append(os.getcwd())
load_dotenv()

from nl_sql import generate_sql
from database import get_db_connection

def debug_revenue_trend():
    question = "Show revenue trend for last 6 months"
    print(f"--- Debugging Question: '{question}' ---")
    
    # 1. Generate SQL
    try:
        sql = generate_sql(question)
        print(f"\n[GENERATED SQL]:\n{sql}")
    except Exception as e:
        print(f"\n[ERROR GENERATING SQL]: {e}")
        return

    # 2. Run SQL
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        print(f"\n[SQL RESULTS ({len(results)} rows)]:")
        df = pd.DataFrame(results, columns=columns)
        print(df)
        conn.close()
    except Exception as e:
        print(f"\n[ERROR EXECUTING SQL]: {e}")

    # 3. Check Base Data
    print("\n--- Checking Base Data in billing_transactions ---")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check count
        cursor.execute("SELECT COUNT(*) FROM billing_transactions")
        count = cursor.fetchone()[0]
        print(f"Total rows in billing_transactions: {count}")
        
        # Check date range
        if count > 0:
            cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM billing_transactions")
            min_date, max_date = cursor.fetchone()
            print(f"Date Range: {min_date} to {max_date}")
            
            # Sample 5 rows
            cursor.execute("SELECT id, grand_total, created_at FROM billing_transactions ORDER BY created_at DESC LIMIT 5")
            samples = cursor.fetchall()
            print("\nLatest 5 Transactions:")
            for s in samples:
                print(s)
        
        conn.close()
    except Exception as e:
        print(f"Error checking base data: {e}")

if __name__ == "__main__":
    debug_revenue_trend()
