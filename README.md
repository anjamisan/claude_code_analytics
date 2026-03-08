# Claude Code Usage Analytics Platform

This project is an analytics platform for Claude Code telemetry, built with FastAPI (backend API), PostgreSQL (data storage), Streamlit (frontend UI), and Plotly (interactive charts).

It supports:
- Loading historical telemetry into PostgreSQL
- Querying aggregated analytics via REST endpoints
- Visualizing usage, cost, tools, errors, and user behavior in Streamlit

## Project Structure

```
claude-code-analytics/
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI route modules
│   │   ├── queries/              # SQL query functions used by API routes
│   │   ├── models/               # SQLModel table + response models
│   │   ├── database.py           # Engine/session + max timestamp cache
│   │   └── main.py               # FastAPI app entrypoint
│   ├── Dockerfile                # Backend container image definition
│   └── requirements.txt
├── frontend/
│   ├── app.py                    # Streamlit app entrypoint
│   ├── api.py                    # HTTP client helpers to call FastAPI
│   ├── views/                    # Streamlit pages/views
│   ├── Dockerfile                # Frontend container image definition
│   └── requirements.txt
├── data/
│   ├── employees.csv             # Employee metadata seed
│   └── telemetry_logs.jsonl      # Telemetry events (JSONL)
├── scripts/
│   ├── generate_fake_data.py     # Generates synthetic telemetry + employee data
│   └── load_data.py              # Loads data files into PostgreSQL tables
├── docker-compose.yml            # PostgreSQL + backend + frontend container setup
└── README.md
```

## Architecture Overview

### 1) Backend (FastAPI)
- API routers are grouped by domain under `backend/app/api`:
  - `overview`, `usage`, `tokens`, `tools`, `errors`, `users`
- Each endpoint delegates SQL work to functions in `backend/app/queries`.
- DB access is managed in `backend/app/database.py` using SQLModel/SQLAlchemy sessions.
- For time-window queries, the backend uses `MAX(event_timestamp)` (cached) as a stable reference for historical datasets.

### 2) Database (PostgreSQL)
- Primary event table: `events`
- Detail tables keyed by `event_id`:
  - `api_requests`, `tool_results`, `tool_decisions`, `user_prompts`, `api_errors`
- Dimension table:
  - `employees`

### 3) Frontend (Streamlit + Plotly)
- `frontend/app.py` provides page navigation.
- Each page in `frontend/views` requests data from FastAPI and renders Plotly charts.
- `frontend/api.py` is the shared HTTP layer to call backend endpoints (`API_BASE` is environment-configurable for Docker networking).

### 4) Data Flow
1. Generate or provide telemetry files in `data/`.
2. Run `scripts/load_data.py` to populate PostgreSQL tables.
3. FastAPI serves aggregated analytics from SQL queries.
4. Streamlit calls API endpoints and renders charts.

## Setup Instructions (Linux)

These instructions are written for Linux.

### Prerequisites
- Python 3.10+
- `pip`
- PostgreSQL 13+ (local) or Docker + Docker Compose

### Option A: Run PostgreSQL and backend with Docker Compose

Note: `docker-compose.yml` contains intentionally hardcoded mock database credentials for this examination assignment and local demo convenience. These are not production secrets. 

1. Clone and enter the repository:
  ```bash
  git clone <repository-url>
  cd claude-code-analytics
  ```

2. Start PostgreSQL + backend API:
  ```bash
  docker compose up --build -d
  ```

3. Wait for first-run initialization to complete (one-time):
  - `data-loader` service automatically generates deterministic demo data and loads it into PostgreSQL.
  - This happens only when the Docker data volume is empty.
  - On first run, this step can take a few minutes.

4. Verify backend is up:
  ```bash
  curl http://localhost:8000/
  ```

5. Open applications:
  - Frontend: `http://localhost:8501`
  - Backend OpenAPI docs: `http://localhost:8000/docs`

6. (Optional) Set up Python virtual environment for local scripts/tooling:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r backend/requirements.txt
  pip install -r frontend/requirements.txt
  ```

To force a full re-initialization (drop DB + regenerated data), run:

```bash
docker compose down -v
docker compose up --build -d
```

### Option B: Run everything locally (no Docker)

1. Clone and enter repository:
  ```bash
  git clone <repository-url>
  cd claude-code-analytics
  ```

2. Create and activate virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

3. Install dependencies:
  ```bash
  pip install -r backend/requirements.txt
  pip install -r frontend/requirements.txt
  ```

4. Create a `.env` file in project root and set DB connection:
  ```bash
  DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db_name>
  FASTAPI_DEBUG=False
  ```

5. Start backend API:
  ```bash
  uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
  ```

### Data Generation and Loading

`telemetry_data.json` / large raw telemetry files are not uploaded to GitHub due to repository size limits.

Use scripts in `/scripts` to generate and load data:

1. Generate synthetic data files:
  ```bash
  source venv/bin/activate
  python scripts/generate_fake_data.py --num-users 100 --num-sessions 5000 --days 60
  ```

2. Load generated (or existing) data into PostgreSQL:
  ```bash
  source venv/bin/activate
  python scripts/load_data.py
  ```

Notes:
- Loader expects files under `data/` (notably `telemetry_logs.jsonl` and `employees.csv`).
- The generator writes compatible files for the loader workflow.
- Docker flow runs generation/loading automatically on first run via the `data-loader` service.

### Start Frontend

Run Streamlit from project root:

```bash
source venv/bin/activate
streamlit run frontend/app.py
```

Then open:
- Frontend: `http://localhost:8501`
- Backend OpenAPI docs: `http://localhost:8000/docs`

## Telemetry Event Types

The telemetry data consists of four event types, each representing a different step in a Claude Code interaction:

| Event | Description | Key Attributes |
|-------|-------------|----------------|
| `user_prompt` | Logged when a user sends a message to Claude Code | `prompt_length` |
| `api_request` | An API call to Anthropic's model for inference | `model`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_creation_tokens`, `cost_usd`, `duration_ms` |
| `tool_decision` | Claude deciding whether to use a tool (accept/reject) | `tool_name`, `decision`, `source` |
| `tool_result` | The outcome of executing a tool on the user's machine | `tool_name`, `success`, `duration_ms` |

### Why only `api_request` has a cost

Only `api_request` events carry a `cost_usd` field because they are the only events that call Anthropic's API — which is where billing occurs (token-based pricing for model inference). The other events are all local operations: the user typing a prompt, Claude making a tool-use decision, or a tool running on the user's machine. None of these involve a paid API call.

### Typical event flow

A single user interaction follows this pattern:

1. **`user_prompt`** — the user sends a message.
2. **`api_request`** — Claude Code calls the model to generate a response.
3. The model may decide to use a tool → **`tool_decision`** → **`tool_result`**.
4. **`api_request`** — Claude processes the tool output and decides what to do next.
5. Steps 3–4 repeat (the **agentic loop**) until Claude produces a final answer.

Because of the agentic loop, a single `user_prompt` is followed by **one or more `api_request` events**. The first API call responds directly to the user's message, while subsequent ones handle intermediate tool results (reading files, writing code, running commands, etc.). This means there are typically many more `api_request` events than `user_prompt` events in any given session.

## Note on Time-Based Queries

The dataset contains static/historical telemetry data (timestamps range from `2025-12-03` to `2026-01-31`). Because of this, all time-windowed queries use `MAX(event_timestamp)` as the reference point instead of `NOW()`. The max timestamp is fetched once and cached in memory (5-minute TTL) to avoid redundant queries.

If the system were to receive **live streaming data**, the `max_ts` caching mechanism would no longer be needed — you would switch to `NOW()` directly in the SQL queries, since the latest event timestamp would always be close to the current server time.

## Dependencies

This project uses two dependency sets.

### Backend (`backend/requirements.txt`)
- FastAPI==0.104.1
- SQLAlchemy==2.0.23
- sqlmodel==0.0.14
- asyncpg==0.29.0
- psycopg2-binary==2.9.9
- pydantic==2.5.0
- uvicorn[standard]==0.24.0
- python-dotenv==1.0.0
- pytest==7.4.3
- httpx==0.25.2
- streamlit==1.29.0

### Frontend (`frontend/requirements.txt`)
- streamlit==1.29.0
- pandas==2.2.3
- numpy==1.26.4
- matplotlib==3.9.2
- seaborn==0.13.2
- plotly==5.24.1
- altair==5.5.0
- requests==2.32.3
- sqlalchemy==2.0.36
- psycopg2-binary==2.9.10

## License

This project is licensed under the MIT License. See the LICENSE file for more details.