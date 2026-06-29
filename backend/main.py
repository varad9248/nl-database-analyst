import os
import asyncpg
from typing import Any, Dict, List
from typing_extensions import TypedDict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

load_dotenv(dotenv_path="../.env")

# ----------------- FastAPI Setup -----------------
app = FastAPI(title="NL-DB Analyst with LangGraph")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- State & Schema Setup -----------------
DB_SCHEMA_CONTEXT = """
Available Tables and Columns:
1. Table 'users'
   - user_id (INT, PRIMARY KEY)
   - name (VARCHAR)
   - email (VARCHAR)
   - join_date (DATE)

2. Table 'products'
   - product_id (INT, PRIMARY KEY)
   - name (VARCHAR)
   - category (VARCHAR)
   - price (DECIMAL)
   - stock (INT)

3. Table 'orders'
   - order_id (INT, PRIMARY KEY)
   - user_id (INT, REFERENCES users)
   - product_id (INT, REFERENCES products)
   - quantity (INT)
   - order_date (DATE)
"""

# Define the state that will be passed between nodes
class AgentState(TypedDict):
    user_query: str
    generated_sql: str
    error_message: str | None
    query_results: List[Dict[str, Any]]
    retry_count: int
    logs: List[str]

# ----------------- Graph Nodes -----------------
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def generate_sql_node(state: AgentState):
    """Generates or repairs the SQL query using the 70B model."""
    query = state["user_query"]
    error = state.get("error_message")
    failed_sql = state.get("generated_sql")
    logs = state.get("logs", [])
    retry_count = state.get("retry_count", 0)

    system_instruction = f"""You are a PostgreSQL expert. Output ONLY raw, executable SQL. No markdown wrappers. 
Schema:
{DB_SCHEMA_CONTEXT}"""

    if error and failed_sql:
        system_instruction += f"\n\nCRITICAL FIX REQUIRED:\nFailed SQL: {failed_sql}\nError: {error}\nAnalyze the PostgreSQL error and fix the syntax or schema mismatch."
        logs.append(f"Attempt {retry_count + 1}: Regenerating SQL to self-heal...")
    else:
        logs.append("Generating initial SQL query...")

    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=query)
    ]

    # LangSmith automatically traces this LLM call
    response = llm.invoke(messages)
    clean_sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
    
    logs.append(f"Agent generated SQL: {clean_sql}")

    return {
        "generated_sql": clean_sql,
        "logs": logs
    }

async def execute_sql_node(state: AgentState):
    """Executes the SQL against Postgres and handles exceptions."""
    sql = state["generated_sql"]
    logs = state.get("logs", [])
    retry_count = state.get("retry_count", 0)
    
    logs.append("Executing query against PostgreSQL sandbox...")
    
    try:
        conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
        records = await conn.fetch(sql)
        results = [dict(r) for r in records]
        await conn.close()
        
        logs.append("Execution successful.")
        return {
            "error_message": None,
            "query_results": results,
            "logs": logs
        }
        
    except asyncpg.PostgresError as e:
        error_msg = str(e)
        logs.append(f"❌ Database Error Caught: {error_msg}")
        return {
            "error_message": error_msg,
            "retry_count": retry_count + 1,
            "logs": logs
        }
    except Exception as e:
        error_msg = str(e)
        logs.append(f"❌ System Error Caught: {error_msg}")
        return {
            "error_message": error_msg,
            "retry_count": retry_count + 1,
            "logs": logs
        }

def route_after_execution(state: AgentState) -> str:
    """Determines which node the graph should transition to next."""
    if state.get("error_message") is None:
        return "success"
    if state.get("retry_count", 0) >= 3:
        return "max_retries_exceeded"
    return "retry"

# ----------------- Build LangGraph -----------------
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("execute_sql", execute_sql_node)

# Add Edges
workflow.add_edge(START, "generate_sql")
workflow.add_edge("generate_sql", "execute_sql")

# Add Conditional Logic for the Self-Healing Loop
workflow.add_conditional_edges(
    "execute_sql",
    route_after_execution,
    {
        "success": END,
        "max_retries_exceeded": END,
        "retry": "generate_sql"
    }
)

app_graph = workflow.compile()

# ----------------- FastAPI Routes -----------------
class QueryPayload(BaseModel):
    prompt: str

@app.post("/api/query")
async def analyze_query(payload: QueryPayload):
    # Initialize the Graph State
    initial_state = {
        "user_query": payload.prompt,
        "generated_sql": "",
        "error_message": None,
        "query_results": [],
        "retry_count": 0,
        "logs": ["Booting LangGraph orchestration engine..."]
    }

    # Execute graph asynchronously
    final_state = await app_graph.ainvoke(initial_state)

    if final_state.get("error_message"):
        raise HTTPException(
            status_code=400, 
            detail={
                "message": "Agent maxed out retries without self-healing.", 
                "logs": final_state["logs"]
            }
        )

    return {
        "status": "success",
        "sql": final_state["generated_sql"],
        "data": final_state["query_results"],
        "logs": final_state["logs"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)