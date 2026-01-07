import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.getcwd())

load_dotenv()

try:
    import ollama
    print("Ollama package found.")
    
    # Try a simple generation
    model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    print(f"Testing model: {model}")
    
    response = ollama.chat(model=model, messages=[
        {'role': 'user', 'content': 'Hello'}
    ])
    print("Response received:", response['message']['content'])

except ImportError:
    print("ERROR: ollama package NOT installed.")
except Exception as e:
    print(f"ERROR: {e}")
