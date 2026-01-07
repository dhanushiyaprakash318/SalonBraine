import os
import sys
from dotenv import load_dotenv
import json

sys.path.append(os.getcwd())
load_dotenv()

from analysis_service import generate_analysis

question = "What are the key trends in salon services?"
# Sample aggregated data
data = [
    {"service_name": "Haircut", "total_revenue": 5000, "total_sold": 50},
    {"service_name": "Facial", "total_revenue": 3000, "total_sold": 20},
    {"service_name": "Manicure", "total_revenue": 1500, "total_sold": 15}
]

print(f"Question: {question}")
print("Generating Insights...")

insights_raw = generate_analysis(question, data)
print("\n--- FINAL INSIGHTS ---")
print(insights_raw)
print("-----------------------")

try:
    parsed = json.loads(insights_raw)
    if "insights" in parsed and isinstance(parsed["insights"], list):
        print("✅ SUCCESS: Valid JSON with insights list found.")
    else:
        print("❌ FAILURE: JSON parsed but 'insights' list missing.")
except json.JSONDecodeError:
    print("❌ FAILURE: Response is not valid JSON.")
