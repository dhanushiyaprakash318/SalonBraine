from database import get_db_connection

def run_test_sql():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = """
    SELECT i.product_id, i.product_name, i.volume, i.min_stock_level
    FROM master_inventory i 
    WHERE CAST(NULLIF(i.volume, '') AS DECIMAL(10,2)) = 0
    """
    
    print(f"Running SQL:\n{sql}")
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        print(f"Rows found: {len(rows)}")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error: {e}")
        
    conn.close()

if __name__ == "__main__":
    run_test_sql()
