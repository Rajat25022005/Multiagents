# 🤖 AgentOS — Multi-Agent Orchestration System

A production-ready, full-stack AI agent system featuring parallel task execution, vector memory, ReAct tool agents, real-time SSE streaming, and a modern React UI.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        React Frontend                        │
│              SSE streaming · Task history · Dark UI          │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP / SSE
┌──────────────────────────▼──────────────────────────────────┐
│                     FastAPI Backend                          │
│   Auth (JWT) · Task Routes · System Routes · Health Check   │
└──┬──────────────┬────────────────┬───────────────────────────┘
   │              │                │
   ▼              ▼                ▼
Celery+Redis  Orchestrator   PostgreSQL
(async jobs)   Engine        (task history)
                  │
        ┌─────────┼──────────┐
        ▼         ▼          ▼
    Planner   Executor    ReAct
    Agent     Agent       Agent
     │            │          │
     │         ChromaDB   Tools:
     │        (vector      search_web
     │         memory)     run_python
     └──────────────────   read_file
              │            write_file
           Neo4j
        (graph memory)
```

---

## 🚀 Quick Start

### Prerequisites
- Docker + Docker Compose
- At least one LLM provider API key (OpenAI, Groq, Gemini) OR local Ollama

### 1. Clone and configure

```bash
git clone <your-repo>
cd multiagent
cp .env.example .env
```

Edit `.env` — at minimum set your LLM provider key:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
DEFAULT_MODEL=gpt-4o-mini
```

### 2. Deploy with Docker Compose

```bash
docker-compose up -d
```

Services start:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474

### 3. First run

1. Open http://localhost:3000
2. Click "Create account"
3. Enter any task and click "Run Task"

---

## 🔧 Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start services
docker-compose up postgres redis neo4j -d

# Run backend
uvicorn main:app --reload --port 8000
```

### Celery Worker (separate terminal)

```bash
cd backend
celery -A workers.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

---

## 🤖 Agent Types

| Agent | Description | Use Case |
|-------|-------------|----------|
| `executor` | General reasoning & writing | Default agent |
| `react` | ReAct loop with tool use | Tasks needing web search, code execution, file ops |
| `code` | Generate + run Python code | Data analysis, automation scripts |
| `search` | Web research + summarization | Research tasks |
| `summarizer` | Synthesize multiple results | Aggregation |

The **Planner Agent** automatically selects the right agent type per subtask.

---

## 🛠 ReAct Tools

Available to the `react` agent:

| Tool | Description |
|------|-------------|
| `search_web(query)` | DuckDuckGo search |
| `read_file(path)` | Read file from disk |
| `write_file(path, content)` | Write file to disk |
| `run_python(code)` | Execute Python in sandbox |
| `list_files(directory)` | List directory contents |
| `http_get(url)` | Fetch any URL |

---

## 📡 API Reference

### Auth
```
POST /auth/register   { email, username, password }
POST /auth/login      { email, password }
GET  /auth/me
```

### Tasks
```
POST /tasks/execute          Queue async task → { job_id }
POST /tasks/execute/stream   Stream task via SSE
GET  /tasks/status/{job_id}  Poll Celery job status
GET  /tasks/                 List user's tasks
GET  /tasks/{id}             Get task details
DELETE /tasks/{id}           Delete task
```

### System
```
GET /system/health   Service health check
GET /system/info     LLM provider info
```

---

## 🔌 LLM Providers

Configure in `.env`:

```env
# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
DEFAULT_MODEL=gpt-4o-mini

# Groq (fast + free tier)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
DEFAULT_MODEL=llama-3.1-70b-versatile

# Google Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
DEFAULT_MODEL=gemini-1.5-flash

# Ollama (local)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2
```

---

## 📊 Observability (Optional)

Add Langfuse for LLM tracing:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## 🐳 Production Deployment

```bash
# Build and push images
docker-compose build
docker-compose push

# Or use Docker Swarm
docker stack deploy -c docker-compose.yml multiagent

# Scale workers
docker-compose up --scale worker=4 -d
```

---

## 📁 Project Structure

```
multiagent/
├── backend/
│   ├── api/
│   │   ├── models/        # SQLAlchemy models + Pydantic schemas
│   │   └── routes/        # FastAPI route handlers
│   ├── agents/
│   │   ├── planner.py     # Task decomposition with structured output
│   │   ├── executor.py    # General + code execution agents
│   │   ├── react_agent.py # ReAct tool-use loop
│   │   └── vector_memory.py # ChromaDB semantic search
│   ├── core/
│   │   ├── llm_router.py  # Unified LLM provider abstraction
│   │   ├── neo4j_client.py # Graph memory
│   │   └── security.py    # JWT auth
│   ├── workers/           # Celery async task workers
│   ├── actions/           # Code sandbox, web scraper, file manager
│   ├── orchestrator/      # Main engine: parallel execution + streaming
│   └── main.py            # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── pages/         # Login, Register, Dashboard, TaskDetail
│   │   ├── components/    # StreamViewer, ResultViewer, Layout
│   │   ├── store/         # Zustand state (auth, tasks)
│   │   └── services/      # Axios API client
│   ├── nginx.conf         # Production nginx with API proxy
│   └── Dockerfile         # Multi-stage build
├── docker-compose.yml
└── .env.example
```
