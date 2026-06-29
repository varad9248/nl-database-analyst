# 🧠 NL-Database Analyst

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![LangChain](https://img.shields.io/badge/LangChain-FFFFFF?style=for-the-badge&logo=chainlink&logoColor=black)](https://langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Workflow-blue?style=for-the-badge)]()
[![Groq](https://img.shields.io/badge/Groq-Llama--3.3--70B-orange?style=for-the-badge)]()

An autonomous, **self-healing AI database analyst** that translates natural language into SQL, executes queries against a PostgreSQL database, and autonomously repairs failed queries using an iterative **ReAct** reasoning loop powered by **LangGraph** and **Llama-3.3-70B**.

The system continuously reasons about execution failures, analyzes PostgreSQL error messages, regenerates improved SQL, and retries until the query succeeds or a retry limit is reached.

---

## 📸 Demo

> Replace this image with your project screenshot.

![NL Database Analyst](docs/hero-ui.png)

---

# ✨ Features

### 🤖 Autonomous Self-Healing

- Detects SQL execution failures automatically.
- Reads PostgreSQL error messages.
- Understands the cause of failure.
- Regenerates corrected SQL.
- Retries execution without user intervention.

Examples of handled failures:

- Ambiguous columns
- Missing aliases
- Hallucinated table names
- Hallucinated columns
- Invalid joins
- Syntax errors

---

### 🧠 Agentic Workflow using LangGraph

The application is designed as a deterministic **state machine** instead of a single LLM call.

Each node performs one responsibility:

- Understand Question
- Generate SQL
- Execute Query
- Detect Errors
- Repair SQL
- Return Results

This makes the workflow:

- explainable
- observable
- debuggable
- production-ready

---

### 🗄️ Schema-Aware SQL Generation

Before generating SQL, the agent dynamically loads the database schema including:

- Tables
- Columns
- Relationships
- Primary Keys
- Foreign Keys

This dramatically reduces hallucinations and improves first-pass SQL accuracy.

---

### 🔄 Intelligent Retry Loop

Instead of immediately failing, the agent:

1. Executes SQL
2. Captures PostgreSQL exception
3. Feeds stack trace back to the LLM
4. Regenerates SQL
5. Retries execution

The retry loop continues until:

- Success
- Maximum retry count reached

---

### 📊 LangSmith Observability

Every agent run is fully traceable through LangSmith.

Track:

- Prompt history
- Node execution
- Token usage
- Latency
- Retry attempts
- State transitions
- Final SQL

Perfect for debugging agent behavior.

---

# 🏗️ System Architecture

The workflow is implemented as a LangGraph state machine.

```mermaid
graph TD

A[User Natural Language Query]
--> B[LangGraph State Engine]

B --> C[Generate SQL]

C -->|Llama-3.3-70B| D[Draft SQL]

D --> E[Execute SQL]

E -->|Success| F[Parse Results]

F --> G[React Data Table]

E -->|PostgreSQL Error| H[Capture Exception]

H --> I[Increment Retry Counter]

I --> C
```

---

# ⚙️ Tech Stack

## AI & Agent Orchestration

- LangGraph
- LangChain
- Groq API
- Llama-3.3-70B-Versatile
- LangSmith

---

## Backend

- FastAPI
- Python 3.12+
- asyncpg
- PostgreSQL
- uv Package Manager
- Pydantic

---

## Frontend

- React
- Vite
- TailwindCSS
- TypeScript

---

## Database

- PostgreSQL
- SQL
- asyncpg

---

## Infrastructure

- Docker
- Docker Compose

---

# 🚀 Getting Started

## 1. Clone Repository

```bash
https://github.com/varad9248/nl-database-analyst.git

cd nl-database-analyst
```

---

## 2. Configure Environment

Create a `.env` file in the project root.

```env
# Groq

GROQ_API_KEY=your_groq_api_key

# PostgreSQL

DATABASE_URL=postgresql://postgres:password@postgres-db:5432/ecommerce

# LangSmith (Optional)

LANGCHAIN_TRACING_V2=true

LANGCHAIN_API_KEY=your_langsmith_key

LANGCHAIN_PROJECT=nl_db_analyst
```

---

## 3. Launch Application

```bash
docker compose up -d
```

On the first startup Docker automatically:

- Creates PostgreSQL database
- Executes `db/init.sql`
- Builds sample ecommerce schema
- Inserts demo data
- Starts backend
- Starts frontend

---

# 🌐 Access the Application

| Service | URL |
|----------|-----|
| Frontend | http://localhost |
| FastAPI Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

---

# 📊 LangSmith Observability

The application integrates with LangSmith for complete execution tracing.

Track:

- Agent reasoning
- SQL generation
- Retry loops
- State transitions
- Prompt versions
- Token usage
- Latency
- Final SQL
- Errors

This makes debugging autonomous agents significantly easier.

---

# 📂 Project Structure

```text
nl-database-analyst/

├── backend/
│   ├── app/
│   ├── graph/
│   ├── agents/
│   ├── database/
│   └── api/
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── services/
│
├── db/
│   ├── init.sql
│   └── seed.sql
│
├── docker-compose.yml
├── Dockerfile
├── .env
└── README.md
```

---


# 📄 License

Distributed under the MIT License.

See the `LICENSE` file for more information.

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

It helps others discover the project and supports future development.
````
