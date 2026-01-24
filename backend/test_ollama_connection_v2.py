
import ollama
import sys

try:
    print("Attempting to connect to Ollama with model 'llama3:8b'...")
    response = ollama.chat(
        model='llama3:8b', 
        messages=[{'role': 'user', 'content': 'Hello, are you working?'}],
    )
    print("Success!")
    print(response['message']['content'])
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
