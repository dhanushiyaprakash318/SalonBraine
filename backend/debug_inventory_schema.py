from database import get_db_connection

def inspect_inventory():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables = ["master_inventory", "billing_trans_inventory"]
    
    with open("schema_debug.txt", "w") as f:
        for t in tables:
            f.write(f"\n--- {t} ---\n")
            try:
                cursor.execute(f"DESCRIBE {t}")
                cols = cursor.fetchall()
                for col in cols:
                    f.write(f"{col[0]} ({col[1]})\n")
            except Exception as e:
                f.write(f"Error: {e}\n")
            
    conn.close()
    print("Schema written to schema_debug.txt")

if __name__ == "__main__":
    inspect_inventory()
