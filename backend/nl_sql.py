import os
import ollama
try:
    from database import get_db_connection
except ImportError:
    from backend.database import get_db_connection
from dotenv import load_dotenv

load_dotenv()

# Configuration
# Default to llama3.2:1b (fast/local), but allow override for smarter models (e.g. llama3.1:8b)
# Default to llama3.2:1b for maximum speed
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

_SCHEMA_CACHE = {} # table_name -> column_list_str
_TABLE_LIST = []

def load_schema_if_needed():
    global _SCHEMA_CACHE, _TABLE_LIST
    if _TABLE_LIST:
        return
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        _TABLE_LIST = [t[0] for t in tables]
        
        for table_name in _TABLE_LIST:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            # Format: table_name.column_name to avoid ambiguity in JOINs
            col_names = [f'{table_name}.{col[0]}' for col in columns]
            _SCHEMA_CACHE[table_name] = f"Table {table_name}: {', '.join(col_names)}"
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error loading schema: {e}")

def get_relevant_schema(question: str) -> str:
    load_schema_if_needed()
    
    question_lower = question.lower()
    meta_map = {
        "master_customer": ["customer", "client", "people", "person"],
        "billing_transactions": ["sale", "revenue", "income", "money", "spent", "bill", "transaction"],
        "billing_trans_summary": ["service", "top services", "revenue", "popular"],
        "master_appointment": ["appointment", "book", "visit"],
        "master_service": ["service", "treatment", "work"],
        "master_employee": ["staff", "employee", "worker", "specialist"],
        "master_inventory": ["inventory", "stock", "product", "item", "never sold"],
        "billing_trans_inventory": ["product", "item", "sold", "never sold"],
        "master_membership": ["membership", "member", "active"]
    }
    
    selected_tables = []
    for table, keywords in meta_map.items():
        if any(kw in question_lower for kw in keywords):
            if table in _TABLE_LIST:
                selected_tables.append(table)
    
    # Always include transactions for revenue/sales related queries
    if any(kw in question_lower for kw in ["revenue", "sale", "income"]):
        selected_tables.extend(["billing_transactions", "billing_trans_summary"])
    
    # Remove duplicates and limit
    selected_tables = list(set([t for t in selected_tables if t in _TABLE_LIST]))[:4]
    
    # Default fallback - use first few tables from actual database
    if not selected_tables:
        selected_tables = _TABLE_LIST[:3] if _TABLE_LIST else []
    
    # Filter to only tables that exist in cache
    selected_tables = [t for t in selected_tables if t in _SCHEMA_CACHE]
    
    if not selected_tables:
        return "No tables available"
            
    schema_subset = "\n".join([_SCHEMA_CACHE[t] for t in selected_tables])
    return schema_subset

def validate_sql_safety(sql: str) -> bool:
    """
    Ensures the SQL query is read-only and clean.
    """
    if not sql:
        return False
        
    sql_upper = sql.upper().strip()
    
    # Check if it starts with valid keywords and NOT markdown
    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH"):
        return False

    # Forbidden keywords for safety
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "REPLACE", "GRANT", "REVOKE", "EXEC", "CALL"]
    for word in forbidden:
        import re
        if re.search(r'\b' + word + r'\b', sql_upper):
            return False
            
    return True

def is_sql_query(text: str) -> bool:
    """Check if the text contains a SELECT or WITH query."""
    import re
    # Look for SELECT or WITH (ignoring case) followed by whitespace
    return bool(re.search(r'\b(SELECT|WITH)\b', text, re.I))

def extract_sql(text: str) -> str:
    """Extract clean SQL from response text, stripping markdown and filler."""
    import re
    import json
    
    # 1. Clean JSON if it exists
    try:
        if "{" in text and "}" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            data = json.loads(text[start:end])
            if isinstance(data, dict) and "sql" in data:
                text = data["sql"]
    except:
        pass

    # 2. Cleanup common hallucinations
    text = re.sub(r'salonpos\.', '', text, flags=re.IGNORECASE)
    text = text.replace('```sql', '').replace('```SQL', '').replace('```', '')
    
    # 3. Find the ACTUAL query (SELECT/WITH until end of line or semicolon)
    # This is more robust against trailing conversational rambling
    matches = re.finditer(r'\b(SELECT|WITH)\b[\s\S]+?(?:;|$)', text, re.IGNORECASE)
    queries = [m.group(0).strip() for m in matches]
    
    if queries:
        # Take the longest one that ends with a semicolon or is at the end of a block
        sql = max(queries, key=len)
    else:
        sql = text.strip()
            
    # Final pass: Strip any remaining trailing text/markdown
    sql = sql.split('\n\n')[0] # Usually rambling starts after a double newline
    sql = sql.split('`')[0]
    sql = sql.rstrip('"} ;').strip()
    
    return sql

def generate_sql(question: str) -> str:
    schema = get_relevant_schema(question)
    
    system_prompt = f"""
    You are an expert MySQL Analyst. Respond ONLY with a JSON object.
    
    BUSINESS RULES:
    - TOP SERVICES? Use `billing_trans_summary` (service_name, grand_total).
    - LOW STOCK? Use `master_inventory` WHERE `volume` < `min_stock_level`. 
    - NEVER SOLD? Use `master_inventory` i LEFT JOIN `billing_trans_inventory` ti ON i.product_id = ti.product_id WHERE ti.id IS NULL.
    - JOIN KEYS:
        - `billing_trans_inventory.product_id` matches `master_inventory.product_id`.
        - `billing_transactions.employee_id` = `master_employee.id`.
        - `billing_transactions.customer_id` = `master_customer.id`.

    STRICT RULES:
    1. NEVER mention errors or problems.
    2. NEVER use the database name "salonpos".
    3. Response MUST start with {{"sql": "SELECT...
    4. Provide NO explanation, NO markdown.

    SCHEMA:
    {schema}

    EXAMPLES:
    User: How many customers?
    {{"sql": "SELECT COUNT(*) FROM master_customer"}}

    User: Top 5 services?
    {{"sql": "SELECT service_name, SUM(grand_total) as revenue FROM billing_trans_summary GROUP BY service_name ORDER BY revenue DESC LIMIT 5"}}
    """

    user_prompt = f"Question: {question}\nRespond with the SQL JSON:"
    
    try:
        print(f"Attempting with Ollama Model: {MODEL_NAME}")
        
        response = ollama.chat(
            model=MODEL_NAME, 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            options={
                'num_predict': 150,  # Limit output to avoid rambling
                'temperature': 0,    # Maximize precision for SQL
            }
        )
        
        response_text = response['message']['content'].strip()
        
        # 1. Try to handle case where model returns raw SQL wrapped in markdown instead of JSON
        if "```" in response_text and is_sql_query(response_text):
            potential_sql = extract_sql(response_text)
            if validate_sql_safety(potential_sql):
                return potential_sql

        # 2. Try JSON path
        import json
        try:
            # Flexible JSON extraction
            json_str = response_text
            if "```json" in response_text:
                json_str = response_text.split("```json")[-1].split("```")[0].strip()
            elif "{" in response_text:
                json_str = response_text[response_text.find("{"):response_text.rfind("}")+1]
            
            data = json.loads(json_str)
            sql = data.get("sql", "").strip()
            
            # If SQL in JSON is wrapped in markdown, clean it
            if "```" in sql:
                sql = extract_sql(sql)
            
            if sql and validate_sql_safety(sql):
                return sql
        except json.JSONDecodeError:
            pass

        # 3. Final Fallback: Is there any SQL in here at all?
        if is_sql_query(response_text):
            final_sql = extract_sql(response_text)
            if validate_sql_safety(final_sql):
                return final_sql
        
        return "" # Return empty string if no valid SQL found

    except Exception as e:
        print(f"Error with Ollama: {e}")
        return f"Error generating SQL: {str(e)}"

def generate_conversational_response(question: str, context: str = None) -> str:
    """
    Generates a conversational response when SQL generation fails or isn't needed.
    This ensures the bot always answers questions, even non-SQL ones.
    
    Workflow: User Question → LLaMA (with schema context) → Natural Language Answer
    """
    schema = get_relevant_schema(question)
    
    system_prompt = f"""
    You are a friendly Salon Management Assistant. Answer questions in clear, regular English for a salon owner.
    
    RULES:
    1. Be warm, professional and helpful.
    2. Use 2-3 sentences of regular English.
    3. Do NOT mention database tables, code, or technical errors (like "SQL", "column mismatch").
    4. If you don't have the data, suggest a different question or explain what data is missing in a non-technical way.

    SCHEMA (for your reference only):
    {schema}
    """
    
    user_prompt = f"Question: {question}"
    if context:
        user_prompt += f"\n\nContext: {context}"
    
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            options={
                'num_predict': 200,  # Enough for a good conversational response
                'temperature': 0.5,  # Balanced creativity
            }
        )
        
        response_text = response['message']['content'].strip()
        return response_text
        
    except Exception as e:
        print(f"Error generating conversational response: {e}")
        # Final fallback
        return f"I understand you're asking: '{question}'. I'm here to help with salon analytics queries. Please try asking about specific metrics, trends, or data summaries that I can query from the database."