import os
import json
import ollama
from dotenv import load_dotenv

load_dotenv()

# Configuration
# Default to llama3.2:1b for maximum speed on insights
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

def generate_analysis(question: str, data: list) -> str:
    """
    Generates a natural language analysis of the provided AGGREGATED data based on the question.
    
    IMPORTANT: This function ONLY receives aggregated data (from SQL queries with COUNT, SUM, AVG, etc.),
    NEVER raw records. The LLM only sees aggregated results, not individual customer records.
    This ensures privacy and follows the workflow requirement.
    """
    if not data:
        # Generate a friendly "no data" response instead of a generic one
        try:
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[{'role': 'system', 'content': f"The user asked about '{question}' but there is no data in the system for this. Explain this in one regular, friendly sentence without being technical. Format: {{\"summary\": \"...\"}}"}]
            )
            res = json.loads(response['message']['content'])
            return res.get("summary", "I couldn't find any records matching that request right now.")
        except:
            return "I couldn't find any records for that specific request in the database."

    # Convert aggregated data to string representation
    # Data is already aggregated from SQL queries (COUNT, SUM, AVG, GROUP BY, etc.)
    # Limit to 50 rows to avoid token limits with 1B models
    data_sample = data[:50] if len(data) > 50 else data
    data_str = str(data_sample)
    if len(data) > 50:
        data_str += f"\n... (and {len(data) - 50} more aggregated records)"

    system_prompt = f"""
    You are a friendly Salon Business Analyst. You receive summary data and translate it into clear, regular English for a salon owner.
    
    RULES:
    1. Respond in 2-3 sentences of regular, friendly English.
    2. Do NOT mention technical terms like SQL, columns, or tables.
    3. Focus on the human meaning of the data (e.g., "Business is booming!" or "You might need to restock soon").
    4. Respond ONLY with a JSON object containing a "summary" field.
    5. NO markdown, NO extra text.

    FORMAT:
    {{"summary": "Your regular English answer here..."}}
    """

    user_prompt = f"""
    User Question: {question}
    Aggregated Results: {data_str}
    
    JSON Output:
    """

    try:
        response = ollama.chat(
            model=MODEL_NAME, 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            options={
                'num_predict': 250,  # Enough for 3-4 insights
                'temperature': 0.3,  # Slight creativity for business language
            }
        )
        response_text = response['message']['content'].strip()
        
        # Parse JSON and extract summary
        try:
            if "{" in response_text:
                json_str = response_text[response_text.find("{"):response_text.rfind("}")+1]
                data_json = json.loads(json_str)
                return data_json.get("summary", response_text)
            return response_text
        except:
            return response_text
    except Exception as e:
        return f"Analysis unavailable due to processing error: {str(e)}"
