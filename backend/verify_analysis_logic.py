import sys
import os
sys.path.append(os.getcwd())

from analysis_service import generate_analysis

# Simulate empty data which triggers the fallback logic
data = []
question = "Which products are low on stock?"

print(f"Question: {question}")
response = generate_analysis(question, data)
print(f"Response: {response}")

if "No low stock items found" in response:
    print("✅ SUCCESS: Correct fallback response triggered.")
else:
    print("❌ FAILURE: Fallback response incorrect.")
