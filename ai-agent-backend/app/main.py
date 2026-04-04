import json
import os
from contextlib import asynccontextmanager

import redis.exceptions
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .ai_engine.langchain_agent import run_agent
from .memory.redis_store import (
    extract_memory,
    get_chat_history,
    get_memory,
    redis_ping,
    save_memory,
    save_message,
)
from .schemas import ChatRequest, ChatResponse
from .service.db import init_db

load_dotenv()

CHAT_HISTORY_MAX = int(os.getenv("CHAT_HISTORY_MAX", "20"))


def _default_cors_origins() -> list[str]:
    return [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if raw:
        return [x.strip() for x in raw.split(",") if x.strip()]
    return _default_cors_origins()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="agentstack-api", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    if not redis_ping():
        raise HTTPException(status_code=503, detail="Redis unavailable")
    return {"status": "ready"}


def _map_upstream_error(exc: Exception) -> HTTPException | None:
    name = type(exc).__name__
    low = str(exc).lower()
    if "insufficient_quota" in low or "exceeded your current quota" in low or ("quota" in low and "billing" in low):
        return HTTPException(
            status_code=429,
            detail=(
                "Model provider quota is exhausted. "
                "Please check your API plan/billing, then try again."
            ),
        )
    if "RateLimit" in name or "ResourceExhausted" in name:
        return HTTPException(status_code=429, detail=str(exc))
    if "AuthenticationError" in name or ("auth" in low and "invalid" in low):
        return HTTPException(status_code=401, detail=str(exc))
    if "timeout" in low or "Connection" in name or "ConnectError" in name or "connection refused" in low:
        return HTTPException(status_code=503, detail=str(exc))
    return None


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    user_id = request.user_id
    message = request.message

    try:
        mem_updates = extract_memory(message)
        save_memory(user_id, mem_updates)
        memory = get_memory(user_id)
        history = get_chat_history(user_id)
        tail = history[-CHAT_HISTORY_MAX:] if CHAT_HISTORY_MAX > 0 else history
        chat_lines = [f"{m['role']}: {m['content']}" for m in tail]
        chat_context = "\n".join(chat_lines)
        memory_context = json.dumps(memory, ensure_ascii=True)

        try:
            agent_out = run_agent(
                message,
                chat_context=chat_context,
                memory_context=memory_context,
            )
        except Exception as exc:
            mapped = _map_upstream_error(exc)
            if mapped:
                raise mapped
            raise

        save_message(user_id, "user", message)
        save_message(user_id, "assistant", agent_out["output"])

        return ChatResponse(
            result=agent_out["output"],
            tool_used=agent_out.get("tool_used"),
            tool_result=agent_out.get("tool_result"),
        )
    except HTTPException:
        raise
    except redis.exceptions.RedisError as exc:
        raise HTTPException(status_code=503, detail=f"Redis error: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        mapped = _map_upstream_error(exc)
        if mapped:
            raise mapped
        raise HTTPException(
            status_code=502,
            detail=f"Failed to process chat request: {exc}",
        ) from exc
