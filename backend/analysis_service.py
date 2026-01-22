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
        # Generate a context-aware friendly response based on the question
        question_lower = question.lower()
        
        # Base message for "no records"
        base_fallback = "Answer not found for this specific query."
        suggestion_suffix = " You might want to ask about overall revenue trends, top services, or low stock alerts."

        # Provide intelligent responses based on question type
        keywords_low_stock = ['low stock', 'stock low', 'out of stock', 'inventory low']
        keywords_never_sold = ['unpopular', 'least popular', 'worst selling', 'never sold', 'not sold', 'zero sales']
        
        if any(keyword in question_lower for keyword in keywords_low_stock):
            return "No low stock items found. All products are currently adequately stocked."
        elif any(keyword in question_lower for keyword in keywords_never_sold):
            return "No unsold products found. All items in your inventory have at least one sale record."
        elif 'revenue' in question_lower or 'sales' in question_lower:
            return f"{base_fallback} No revenue data was found for the requested criteria. Try asking for 'Total Revenue' or 'Monthly Sales' instead."
        elif 'customer' in question_lower:
            return f"{base_fallback} No customer records found matching that criteria. You can ask for 'Total Customers' or 'Recent Visits'."
        else:
            # Try to use LLM for more nuanced responses
            try:
                response = ollama.chat(
                    model=MODEL_NAME,
                    messages=[{
                        'role': 'user', 
                        'content': f"User asked: '{question}' but the database returned no results. In 1-2 friendly sentences, explain that the answer wasn't found and suggest 2 related salon metrics they could ask about. Reply with JSON: {{\"summary\": \"your response here\"}}"
                    }],
                    options={'num_predict': 60, 'temperature': 0.3}
                )
                content = response['message']['content'].strip()
                # Clean markdown
                if "```" in content:
                    content = content.replace("```json", "").replace("```", "").strip()
                
                if '{' in content and '}' in content:
                    json_str = content[content.find("{"):content.rfind("}")+1]
                    res = json.loads(json_str)
                    return res.get("summary", f"{base_fallback}{suggestion_suffix}")
            except:
                pass
            
            return f"{base_fallback}{suggestion_suffix}"

    # Convert aggregated data to string representation
    # Data is already aggregated from SQL queries (COUNT, SUM, AVG, GROUP BY, etc.)
    # Limit to 50 rows to avoid token limits with 1B models
    data_sample = data[:50] if len(data) > 50 else data
    data_str = str(data_sample)
    if len(data) > 50:
        data_str += f"\n... (and {len(data) - 50} more aggregated records)"

    system_prompt = f"""
    You are a Business Analyst. Summary for: {question}.
    Respond ONLY with JSON: {{"summary": "..."}}.
    MAX ONE short sentence. Friendly but concise.
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
                'num_predict': 50,
                'temperature': 0,
                'stop': ["}", "\n"]
            }
        )
        response_text = response['message']['content'].strip()
        
        # Parse JSON and extract summary
        try:
            # Clean markdown
            if "```" in response_text:
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            if "{" in response_text:
                json_str = response_text[response_text.find("{"):response_text.rfind("}")+1]
                data_json = json.loads(json_str)
                return data_json.get("summary", response_text)
            return response_text
        except:
            return response_text
    except Exception as e:
        return f"Analysis unavailable due to processing error: {str(e)}"
