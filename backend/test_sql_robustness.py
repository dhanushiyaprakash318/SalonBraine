from nl_sql import extract_sql, validate_sql_safety

test_cases = [
    "```sql\nSELECT * FROM customers\n```",
    "Sure! Here is your query:\n```sql\nSELECT COUNT(*) FROM master_customer;\n```",
    "{\"sql\": \"SELECT * FROM master_service\"}",
    "```\nSELECT * FROM master_employee\n```",
    "SELECT * FROM master_customer ``` some trailing garbage",
    "DROP TABLE students", # Should fail validation
    "INSERT INTO customers VALUES (1, 'Alice')", # Should fail validation
    "```sql\nUPDATE customers SET name = 'Bob'\n```" # Should fail validation
]

def run_tests():
    print("Testing SQL Cleaning & Safety Tests...")
    for i, case in enumerate(test_cases, 1):
        clean = extract_sql(case)
        is_safe = validate_sql_safety(clean)
        print(f"\nTest {i}:")
        print(f"  Input: {case!r}")
        print(f"  Cleaned: {clean!r}")
        print(f"  Is Safe: {is_safe}")

if __name__ == "__main__":
    run_tests()
