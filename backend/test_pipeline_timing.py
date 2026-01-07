import time
import os
import sys
import json
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from nl_sql import generate_sql, is_sql_query
from sql_runner import run_sql_query
from analysis_service import generate_analysis

def test_full_pipeline_timed(question):
    print(f"🔍 Testing pipeline for: '{question}'")
    timings = {}
    
    # 1. SQL Generation
    print("AI generating SQL...")
    start = time.time()
    sql = generate_sql(question)
    timings['sql_gen'] = time.time() - start
    print(f"✅ SQL Gen took: {timings['sql_gen']:.2f}s")
    print(f"SQL: {sql}")
    
    if is_sql_query(sql):
        # 2. SQL Execution
        print("Executing SQL...")
        start = time.time()
        data = run_sql_query(sql)
        timings['sql_exec'] = time.time() - start
        print(f"✅ SQL Exec took: {timings['sql_exec']:.2f}s")
        
        # 3. Insight Generation
        print("AI generating insights...")
        start = time.time()
        insights_raw = generate_analysis(question, data)
        timings['insight_gen'] = time.time() - start
        print(f"✅ Insight Gen took: {timings['insight_gen']:.2f}s")
    else:
        print("❌ Not a SQL query, skipping execution and insights.")
        timings['sql_exec'] = 0
        timings['insight_gen'] = 0
        
    total = sum(timings.values())
    print(f"\nTOTAL PIPELINE TIME: {total:.2f}s")
    return timings

if __name__ == "__main__":
    test_full_pipeline_timed("How many customers are in the database?")
