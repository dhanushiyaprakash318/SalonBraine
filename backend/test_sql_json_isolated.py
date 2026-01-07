import os
import sys
import ollama
import json
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

schema = "Table customers: id, name, email"

system_prompt = f"""
You are an expert SQL Analyst.
Respond ONLY in this exact JSON format:
{{
  "sql": "SELECT ..."
}}
No explanation, no markdown.

SCHEMA:
{schema}
"""

question = "How many customers?"
user_prompt = f"Question: {question}\nRespond with the SQL JSON:"

print(f"Testing with model: {MODEL_NAME}")
try:
    response = ollama.chat(model=MODEL_NAME, messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt},
    ])
    
    response_text = response['message']['content'].strip()
    print("\n--- RAW RESPONSE ---")
    print(response_text)
    print("--------------------")
    
    try:
        data = json.loads(response_text)
        print("✅ SUCCESS: Parsed JSON successfully.")
        print("SQL:", data.get("sql"))
    except:
        print("❌ FAILURE: JSON parsing failed.")

except Exception as e:
    print(f"Error: {e}")
