from database import get_db_connection
import decimal

def check_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    with open("inventory_data_results.txt", "w", encoding="utf-8") as f:
        f.write("Checking first 10 products in master_inventory:\n")
        cursor.execute("SELECT product_name, volume, min_stock_level FROM master_inventory LIMIT 10")
        rows = cursor.fetchall()
        for row in rows:
            name, vol, min_stock = row
            f.write(f"Product: {name:30} | Volume: {str(vol):10} | Min Stock: {min_stock}\n")
        
        f.write("\nChecking for products where volume < min_stock_level:\n")
        try:
            cursor.execute("""
                SELECT product_name, volume, min_stock_level 
                FROM master_inventory 
                WHERE CAST(NULLIF(volume, '') AS DECIMAL(10,2)) < min_stock_level
                LIMIT 10
            """)
            rows = cursor.fetchall()
            if not rows:
                f.write("No products found where volume < min_stock_level using CAST.\n")
            else:
                for row in rows:
                    name, vol, min_stock = row
                    f.write(f"LOW STOCK -> Product: {name:30} | Volume: {str(vol):10} | Min Stock: {min_stock}\n")
        except Exception as e:
            f.write(f"Error during query: {e}\n")

    conn.close()
    print("Data check completed. See inventory_data_results.txt")

if __name__ == "__main__":
    check_data()
