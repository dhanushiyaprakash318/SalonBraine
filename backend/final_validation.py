from nl_sql import generate_sql

questions = [
    "Which products are low on stock?",
    "Show all products",
    "What is the total revenue?"
]

with open("final_validation_results.txt", "w", encoding="utf-8") as f:
    for q in questions:
        f.write(f"Question: {q}\n")
        sql = generate_sql(q)
        f.write(f"SQL: {sql}\n\n")

print("Validation completed. Check final_validation_results.txt")
