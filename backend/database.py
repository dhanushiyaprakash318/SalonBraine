import mysql.connector

def get_db_connection():
    print("[OK] DATABASE CONNECTED")
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="dhanu1837",
        database="salonpos"
    )

