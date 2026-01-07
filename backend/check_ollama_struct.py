
import ollama
try:
    models_info = ollama.list()
    print(models_info)
except Exception as e:
    print(f"Error: {e}")
