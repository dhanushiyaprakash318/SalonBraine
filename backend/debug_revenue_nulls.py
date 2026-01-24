import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from database import get_db_connection
from nl_sql import generate_sql
from sql_runner import run_sql_query

def debug_revenue():
    print("--- DEBUGGING REVENUE DATA ---")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Check Date Range
    print("\n1. Date Range in billing_transactions:")
    cursor.execute("SELECT MIN(created_at) as first_date, MAX(created_at) as last_date, COUNT(*) as count FROM billing_transactions")
    print(cursor.fetchall())
    
    # 2. Check This Month (Jan 2026)
    print("\n2. Data for This Month (Jan 2026):")
    # Note: System time is 2026-01-23, so we check MONTH=1, YEAR=2026
    cursor.execute("SELECT * FROM billing_transactions WHERE MONTH(created_at) = 1 AND YEAR(created_at) = 2026 LIMIT 5")
    rows = cursor.fetchall()
    print(f"Rows found: {len(rows)}")
    if rows:
        print(rows)
        
    # 3. SQL Generation for Comparison
    print("\n3. Generated SQL for 'Compare revenue':")
    sql = generate_sql("compare this month revenue with last month")
    print(f"SQL: {sql}")
    
    # 4. Run the generated SQL
    if sql:
        print("\n4. Execution Result:")
        results = run_sql_query(sql)
        for r in results:
            print(r)
            
    cursor.close()
    conn.close()

if __name__ == "__main__":
    debug_revenue()
