import os
import ollama
from database import get_db_connection
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
        "master_customer": ["customer", "client", "people", "person", "birthday", "anniversary", "membership", "balance", "visit"],
        "billing_transactions": ["bill", "billing", "sale", "revenue", "income", "money", "spent", "transaction", "discount", "tax"],
        "billing_trans_summary": ["service", "top service", "popular", "qty", "spending"],
        "appointment_transactions": ["appointment", "booking", "slot", "pending", "confirmed", "cancelled", "completed", "balance_due", "payment mode", "peak hour", "busiest"],
        "appointment_trans_summary": ["appointment", "booking", "service", "appointment date"],
        "master_service": ["service", "treatment", "work"],
        "master_employee": ["staff", "employee", "worker", "specialist"],
        "master_inventory": ["inventory", "stock", "product", "item", "never sold", "low stock"],
        "billing_trans_inventory": ["product", "item", "sold", "never sold"]
    }
    
    selected_tables = []
    for table, keywords in meta_map.items():
        if any(kw in question_lower for kw in keywords):
            if table in _TABLE_LIST:
                selected_tables.append(table)
    
    # Always include billing tables for revenue/sales related queries
    if any(kw in question_lower for kw in ["revenue", "sale", "income", "spending"]):
        selected_tables.extend([t for t in ["billing_transactions", "billing_trans_summary"] if t in _TABLE_LIST])
    
    # Remove duplicates and limit to a reasonable set
    selected_tables = list(dict.fromkeys([t for t in selected_tables if t in _TABLE_LIST]))[:6]
    
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

def preprocess_question(question: str) -> str:
    """
    Simple rule-based preprocessor to fix common typos and normalize input.
    """
    # Map of common typos/abbreviations to correct terms
    corrections = {
        "compae": "compare",
        "compar": "compare",
        "vs": "compare",
        "versus": "compare",
        "rvnue": "revenue",
        "revnue": "revenue",
        "revenu": "revenue",
        "custmer": "customer",
        "cutomer": "customer",
        "biling": "billing",
        "transac": "transaction"
    }
    
    words = question.split()
    fixed_words = [corrections.get(w.lower(), w) for w in words]
    return " ".join(fixed_words)

def generate_sql(question: str) -> str:
    # 1. Preprocess the question to fix typos
    question = preprocess_question(question)
    
    # 2. DETERMINISTIC RULES (Fast Path for complex common queries)
    # Revenue Comparison: "Compare this month revenue with last month"
    # Uses 'created_at' and robust UNION ALL structure
    if "compare" in question.lower() and "revenue" in question.lower() and "month" in question.lower():
        return "SELECT 'This Month' as period, COALESCE(SUM(grand_total), 0) as revenue FROM billing_transactions WHERE MONTH(created_at) = MONTH(CURDATE()) AND YEAR(created_at) = YEAR(CURDATE()) UNION ALL SELECT 'Last Month', COALESCE(SUM(grand_total), 0) FROM billing_transactions WHERE MONTH(created_at) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND YEAR(created_at) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) UNION ALL SELECT 'Last Year', COALESCE(SUM(grand_total), 0) FROM billing_transactions WHERE YEAR(created_at) = YEAR(CURDATE()) - 1 UNION ALL SELECT 'Total', COALESCE(SUM(grand_total), 0) FROM billing_transactions"
    
    schema = get_relevant_schema(question)
    
    system_prompt = f"""
    You are a strict MySQL generator. Respond ONLY with JSON {{"sql": "..."}}.
    
    COLUMNS & JOINS:
    - master_customer: customer_name, gender, visitcnt
    - master_inventory: product_id, product_name, volume, min_stock_level
    - billing_trans_inventory: product_id, qty, grand_total
    - JOIN: master_inventory.product_id = billing_trans_inventory.product_id
    
    GOLDEN PATTERNS (STRICT):
    - CUSTOMER PROFILE: SELECT * FROM master_customer WHERE customer_name LIKE '%Customer Name%'
    - CUSTOMER SPENDING: SELECT SUM(grand_total) as spending FROM billing_transactions WHERE customer_name LIKE '%Customer Name%'
    - CUSTOMER VISITS: SELECT visitcnt FROM master_customer WHERE customer_name LIKE '%Customer Name%'
    - LOW STOCK: SELECT product_name, volume, min_stock_level FROM master_inventory WHERE CAST(NULLIF(volume, '') AS DECIMAL(10,2)) < min_stock_level
    - NEVER SOLD: SELECT i.product_name FROM master_inventory i LEFT JOIN billing_trans_inventory ti ON i.product_id = ti.product_id WHERE ti.id IS NULL
    - TOP REVENUE: SELECT service_name, SUM(grand_total) as revenue FROM billing_trans_summary GROUP BY service_id, service_name ORDER BY revenue DESC LIMIT 5
    - REVENUE TREND: SELECT DATE_FORMAT(created_at, '%Y-%m') as month, SUM(grand_total) as revenue FROM billing_transactions WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) GROUP BY month ORDER BY month DESC
    - COMPARISON (Revenue): SELECT 'This Month' as period, SUM(grand_total) as revenue FROM billing_transactions WHERE MONTH(created_at) = MONTH(CURDATE()) AND YEAR(created_at) = YEAR(CURDATE()) UNION ALL SELECT 'Last Month', SUM(grand_total) FROM billing_transactions WHERE MONTH(created_at) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND YEAR(created_at) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) UNION ALL SELECT 'Last Year', SUM(grand_total) FROM billing_transactions WHERE YEAR(created_at) = YEAR(CURDATE()) - 1 UNION ALL SELECT 'Total', SUM(grand_total) FROM billing_transactions
    
    RULES:
    1. Response MUST be valid JSON: {{"sql": "SELECT..."}}
    2. NO explanation. NO markdown.
    3. Use MySQL syntax.
    4. For customer name searches, ALWAYS use LIKE '%name%' instead of '=' to handle spaces and partial matches.
    5. For "comparison", "growth", or "trends" between periods, use UNION ALL to show multiple data points.
    6. Always use created_at for revenue time filters.
    
    SCHEMA:
    {schema}
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
                'num_predict': 400,  # Limit output to avoid rambling
                'temperature': 0,    # Maximize precision for SQL
                'stop': ["}"]        # Force JSON completion
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
            
            # If the model rambled and stop sequence didn't catch it, try to clean
            if "sql" in data and isinstance(data["sql"], str):
                 return extract_sql(data["sql"])
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
    You are a friendly Salon Management Assistant. 
    
    CORE GOALS:
    1. If you can answer the question based on the schema, do so concisely.
    2. If you CANNOT answer (missing data, non-salon question, vague), say "Answer not found for this specific query" and then suggest 2-3 RELATED things they COULD ask about (e.g., revenue trends, low stock, top services).
    3. Be warm, professional and helpful.
    4. Keep it to 2 compact sentences max.
    
    RULES:
    - NO technical terms (SQL, columns, tables, database, schema).
    - NO markdown, NO code blocks.

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
                'num_predict': 80,  # Limit for 2 sentences
                'temperature': 0,    # No creativity for conversational either
                'stop': ["\n"]       # Force cut-off
            }
        )
        
        response_text = response['message']['content'].strip()
        return response_text
        
    except Exception as e:
        print(f"Error generating conversational response: {e}")
        # Final fallback
        return f"I understand you're asking: '{question}'. I'm here to help with salon analytics queries. Please try asking about specific metrics, trends, or data summaries that I can query from the database."