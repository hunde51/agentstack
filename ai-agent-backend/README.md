# ai-agent-backend

FastAPI service: LangChain tool-calling agent, Redis chat history + memory, SQLite users, Open-Meteo weather.

## Run locally

1. Start Redis: `redis-server` or `docker run -p 6379:6379 redis:7-alpine`
2. Copy `.env.example` → `.env` and set `OPENAI_API_KEY` or `GEMINI_API_KEY` / `LLM_PROVIDER`.
3. Install: `pip install -r requirements.txt`
4. From this directory: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## Docker Compose

From this directory (set API keys in environment):

`docker compose up --build`

## Endpoints

- `GET /health` — process up
- `GET /ready` — Redis reachable
- `POST /chat` — body `{ "user_id": string, "message": string }` → `{ "result", "tool_used"?, "tool_result"? }`

## Tests

`pip install -r requirements-dev.txt` then `pytest`
