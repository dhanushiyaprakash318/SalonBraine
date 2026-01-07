from insights_service import get_insights
import json
import datetime

# Helper for date serialization
def my_converter(o):
    if isinstance(o, datetime.datetime) or isinstance(o, datetime.date):
        return o.__str__()

print("🔍 Fetching Insights...")
try:
    data = get_insights()
    print(json.dumps(data, indent=2, default=my_converter))
    
    # Check emptiness
    params = ["top_services", "top_customers", "churn_risk", "anomalies", "revenue_trend"]
    empty_params = [p for p in params if not data.get(p)]
    
    if empty_params:
        print(f"\n⚠️ The following sections are empty: {empty_params}")
    else:
        print("\n✅ All sections have data.")

except Exception as e:
    print(f"❌ Error: {e}")
