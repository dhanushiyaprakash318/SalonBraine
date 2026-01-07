from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

try:
    from nl_sql import generate_sql
    from sql_runner import run_sql_query
except ImportError:
    from backend.nl_sql import generate_sql
    from backend.sql_runner import run_sql_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "Backend running"}

@app.post("/query")
def query_data(q: Query):
    """
    Workflow:
    1. User Question → LLaMA (with schema only) → SQL
    2. SQL Validator (SELECT only)
    3. Database → Returns Aggregated Result
    4. Visualization Engine → Charts
    5. LLaMA (Optional) → Insight Summary from aggregated data
    """
    try:
        from nl_sql import validate_sql_safety, generate_conversational_response
        from sql_runner import run_sql_query
        from analysis_service import generate_analysis
        import json
        
        # Step 1: Generate SQL using LLaMA with schema only
        sql_response = generate_sql(q.question)
        
        # Step 2: Validate SQL safety
        if validate_sql_safety(sql_response):
            try:
                # Step 3: Execute SQL and get aggregated results
                data = run_sql_query(sql_response)
                
                # Step 4 & 5: Generate insights from aggregated data
                insights_text = generate_analysis(q.question, data)
                
                return {
                    "question": q.question,
                    "sql": sql_response,
                    "data": data,
                    "answer": insights_text,
                    "status": "success"
                }
            except Exception as db_error:
                print(f"[ERROR] Database execution error: {db_error}")
                # If SQL execution fails, provide conversational response
                conversational_response = generate_conversational_response(
                    q.question, 
                    f"Query execution failed: {str(db_error)}"
                )
                return {
                    "question": q.question,
                    "sql": sql_response,
                    "data": [],
                    "answer": conversational_response,
                    "error": str(db_error),
                    "status": "sql_error"
                }
        else:
            # Step 1 (fallback): SQL generation failed or returned empty string
            # Just get a friendly natural language response based on the question
            conversational_response = generate_conversational_response(q.question)
            
            return {
                "question": q.question,
                "sql": None,
                "data": [],
                "answer": conversational_response,
                "status": "conversational"
            }
            
    except Exception as e:
        print(f"[ERROR] Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Always provide a response, even on error
        try:
            from nl_sql import generate_conversational_response
            error_response = generate_conversational_response(
                q.question, 
                f"An error occurred while processing your question: {str(e)}"
            )
            return {
                "question": q.question,
                "sql": None,
                "data": [],
                "answer": error_response,
                "error": str(e),
                "status": "error"
            }
        except:
            # Final fallback if even conversational generation fails
            return {
                "question": q.question,
                "sql": None,
                "data": [],
                "answer": "I apologize, but I encountered an error processing your question. Please try rephrasing it.",
                "error": str(e),
                "status": "error"
            }

@app.get("/insights")
def get_dashboard_insights():
    print("[INFO] Received /insights request")
    try:
        from insights_service import get_insights
        print("[INFO] Fetching insights data...")
        data = get_insights()
        print("[OK] Insights data fetched successfully")
        return data
    except Exception as e:
        print(f"[ERROR] Error in /insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))
