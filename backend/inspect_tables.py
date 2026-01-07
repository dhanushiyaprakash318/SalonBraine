from database import get_db_connection

def inspect():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables_to_check = ["billing_trans_inventory", "trans_income_expense", "billing_transactions"]
    
    for t in tables_to_check:
        print(f"\n--- {t} ---")
        try:
            cursor.execute(f"DESCRIBE {t}")
            for col in cursor.fetchall():
                print(col)
        except Exception as e:
            print(f"Error: {e}")
            
    conn.close()

if __name__ == "__main__":
    inspect()
