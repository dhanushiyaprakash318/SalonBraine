from nl_sql import generate_sql
import json

question = "Which products are low on stock?"
sql = generate_sql(question)
with open("results_low_stock.txt", "w", encoding="utf-8") as f:
    f.write(f"Generated SQL for '{question}':\n")
    f.write(sql)

