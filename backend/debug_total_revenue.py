import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from sql_runner import run_sql_query
from nl_sql import generate_sql

def debug_total_revenue():
    print("--- DEBUGGING TOTAL REVENUE ---")
    
    # 1. Ask the chatbot what IT thinks
    q = "total revenue"
    generated_sql = generate_sql(q)
    print(f"\n1. Generated SQL for '{q}':")
    print(generated_sql)
    if generated_sql:
        res = run_sql_query(generated_sql)
        print(f"Result: {res}")

    # 2. Run raw queries to find the truth (3078.5) and the error (350)
    print("\n2. RAW QUERIES:")
    
    queries = [
        ("Grand Total (No filters)", "SELECT SUM(grand_total) as val FROM billing_transactions"),
        ("With billstatus='Y'", "SELECT SUM(grand_total) as val FROM billing_transactions WHERE billstatus='Y'"),
        ("With billstatus IS NULL", "SELECT SUM(grand_total) as val FROM billing_transactions WHERE billstatus IS NULL"),
        ("With billstatus!='C' (Not Cancelled)", "SELECT SUM(grand_total) as val FROM billing_transactions WHERE billstatus != 'C'"),
        ("Using billing_trans_summary instead", "SELECT SUM(grand_total) as val FROM billing_trans_summary"),
        ("This Month Only", "SELECT SUM(grand_total) as val FROM billing_transactions WHERE MONTH(created_at)=MONTH(CURDATE()) AND YEAR(created_at)=YEAR(CURDATE())"),
    ]
    
    for label, sql in queries:
        try:
            data = run_sql_query(sql)
            print(f"  {label}: {data[0]}")
        except Exception as e:
            print(f"  {label}: ERROR {e}")

if __name__ == "__main__":
    debug_total_revenue()
