
from database import get_db_connection

def find_customer(name):
    print(f"Searching for customer like '{name}'...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT customer_name FROM master_customer WHERE customer_name LIKE %s", (f"%{name}%",))
        results = cursor.fetchall()
        if results:
            print("Found customers:")
            for r in results:
                print(f"- {r[0]}")
        else:
            print("No customers found.")
        
        # Also check all customers just in case
        cursor.execute("SELECT customer_name FROM master_customer LIMIT 10")
        others = cursor.fetchall()
        print("\nSample customers in DB:")
        for o in others:
            print(f"- {o[0]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_customer("raj")
