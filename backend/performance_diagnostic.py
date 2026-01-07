import time
import os
import sys
from dotenv import load_dotenv
import ollama

sys.path.append(os.getcwd())
load_dotenv()

from nl_sql import validate_sql_safety, is_sql_query, extract_sql, MODEL_NAME

def diagnostic():
    print("🚀 Starting Performance Diagnostics...")
    
    # 1. Test 1B Model (Fast)
    print("\n--- Testing llama3.2:1b ---")
    start = time.time()
    try:
        response = ollama.chat(model="llama3.2:1b", messages=[{'role': 'user', 'content': 'Is 1+1=2? Respond with Yes or No.'}])
        print(f"⏱️ 1B Response time: {time.time() - start:.2f}s")
        print(f"Response: {response['message']['content'].strip()}")
    except Exception as e:
        print(f"❌ 1B Error: {e}")

    # 3. Test 3B Model (Smart)
    print("\n--- Testing llama3.2:3b ---")
    start = time.time()
    try:
        response = ollama.chat(model="llama3.2:3b", messages=[{'role': 'user', 'content': 'Is 1+1=2? Respond with Yes or No.'}])
        print(f"⏱️ 3B Response time: {time.time() - start:.2f}s")
        print(f"Response: {response['message']['content'].strip()}")
    except Exception as e:
        print(f"❌ 3B Error: {e}")

    # 4. End-to-End SQL Gen (Two-Pass with 1B)
    print("\n--- Testing E2E SQL Gen (Surgical Schema) ---")
    from nl_sql import generate_sql
    start = time.time()
    sql = generate_sql("How many customers?")
    print(f"⏱️ E2E SQL Gen: {time.time() - start:.2f}s")
    print(f"SQL: {sql}")

if __name__ == "__main__":
    diagnostic()
