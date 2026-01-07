
import mysql.connector
import ollama
import requests

def check_mysql():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dhanu1837",
            database="salonpos"
        )
        print("[OK] MySQL connected successfully.")
        conn.close()
    except Exception as e:
        print(f"[ERROR] MySQL connection failed: {e}")

def check_ollama():
    try:
        response = ollama.list()
        # The structure is objects with a 'model' attribute
        available_models = [m.model for m in response.models]
        print(f"[OK] Ollama is running. Available models: {available_models}")
        if any("llama3.2:1b" in m for m in available_models):
            print("[OK] llama3.2:1b is available.")
        else:
            print("[WARNING] llama3.2:1b not found.")
    except Exception as e:
        print(f"[ERROR] Ollama check failed: {e}")

def check_backend():
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        print(f"[OK] Backend response: {response.json()}")
    except Exception as e:
        print(f"[BACKEND NOT RUNNING] {e}")

if __name__ == "__main__":
    print("--- Health Check ---")
    check_mysql()
    check_ollama()
    check_backend()
