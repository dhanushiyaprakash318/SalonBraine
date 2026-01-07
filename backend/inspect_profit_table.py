from database import get_db_connection

def inspect():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        print("--- trans_income_expense ---")
        cursor.execute("DESCRIBE trans_income_expense")
        for col in cursor.fetchall():
            print(col)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect()
