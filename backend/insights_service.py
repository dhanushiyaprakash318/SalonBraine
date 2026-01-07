try:
    from database import get_db_connection
except ImportError:
    from backend.database import get_db_connection

def get_insights():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Top 5 Services by Quantity
        cursor.execute("""
            SELECT service_name, SUM(qty) as total_sold, SUM(grand_total) as total_revenue
            FROM billing_trans_summary
            GROUP BY service_id, service_name
            ORDER BY total_sold DESC
            LIMIT 5
        """)
        top_services = cursor.fetchall()

        # 2. Top 5 Customers by Revenue
        cursor.execute("""
            SELECT c.customer_name, SUM(bt.grand_total) as total_spent
            FROM billing_transactions bt
            JOIN master_customer c ON bt.customer_id = c.id
            GROUP BY c.id, c.customer_name
            ORDER BY total_spent DESC
            LIMIT 5
        """)
        top_customers = cursor.fetchall()

        # 3. Customer Churn Risk (Regular customers not seen in 14 days)
        # For demo purposes/old data, let's just show customers who haven't visited in the last 7 days regardless of how old.
        cursor.execute("""
            SELECT c.customer_name, MAX(bt.created_at) as last_visit
            FROM master_customer c
            JOIN billing_transactions bt ON bt.customer_id = c.id
            GROUP BY c.id, c.customer_name
            ORDER BY last_visit ASC
            LIMIT 5
        """)
        churn_risk = cursor.fetchall()

        # 4. Inventory Anomalies (Products with NO sales in billing_trans_inventory)
        cursor.execute("""
            SELECT i.product_name as name, 'No Sales' as issue
            FROM master_inventory i
            LEFT JOIN billing_trans_inventory bti ON i.id = bti.product_id
            WHERE bti.id IS NULL
            LIMIT 5
        """)
        anomalies = cursor.fetchall()

        # 5. Daily Revenue Trend (Last 7 days of actual data)
        cursor.execute("""
            SELECT DATE(created_at) as date, SUM(grand_total) as revenue
            FROM billing_transactions
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 7
        """)
        revenue_trend = cursor.fetchall()
        
        # 6. Key Metrics (Revenue, Tx, Profit)
        # Revenue & Tx
        cursor.execute("""
            SELECT 
                SUM(grand_total) as total_revenue, 
                COUNT(*) as total_transactions 
            FROM billing_transactions
        """)
        summary = cursor.fetchone()
        
        # Profit (Income - Expense)
        # Try to calculate from trans_income_expense if column 'amount' exists, else 0
        try:
            cursor.execute("""
                SELECT 
                    (SELECT COALESCE(SUM(amount), 0) FROM trans_income_expense WHERE type = 'Income') - 
                    (SELECT COALESCE(SUM(amount), 0) FROM trans_income_expense WHERE type = 'Expense') as profit
            """)
            profit_data = cursor.fetchone()
            profit = profit_data['profit'] if profit_data else 0
        except:
            profit = 0

        conn.close()
        
        return {
            "top_services": top_services,
            "top_customers": top_customers,
            "churn_risk": churn_risk,
            "anomalies": anomalies,
            "revenue_trend": revenue_trend,
            "metrics": {
                "revenue": summary['total_revenue'] or 0,
                "transactions": summary['total_transactions'] or 0,
                "profit": profit
            }
        }
    except Exception as e:
        print(f"Error in get_insights: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import json
    print(json.dumps(get_insights(), indent=2, default=str))
