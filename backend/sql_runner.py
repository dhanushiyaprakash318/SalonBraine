from database import get_db_connection

def run_sql_query(sql: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data
