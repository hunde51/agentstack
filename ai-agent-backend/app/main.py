import json
from fastapi import FastAPI, HTTPException
from .schemas import ChatRequest
from .ai_engine import get_ai_response
from .service import get_users, get_weather
from .memory import extract_memory, get_chat_history, get_memory, save_memory, save_message

app = FastAPI()


def _clean_json_text(raw_text: str) -> str:
    text = (raw_text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return text.strip()


def execute_action(action: str, params: dict):
    if action == "get_users":
        return get_users()

    if action == "get_weather":
        city = params.get("city")
        if not city:
            raise HTTPException(status_code=400, detail="Missing 'city' in params for get_weather.")
        return get_weather(city)

    raise HTTPException(status_code=400, detail=f"Unsupported action: {action}")

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        # 1) Save the incoming user message.
        save_message(user_id=request.user_id, role="user", content=request.message)

        # 2) Extract and persist long-term facts when available.
        memory_update = extract_memory(request.message)
        save_memory(user_id=request.user_id, memory_update=memory_update)

        # 3) Build LLM context from short-term and long-term memory.
        history = get_chat_history(request.user_id)
        long_term_memory = get_memory(request.user_id)

        # 4) Ask the model for a structured action decision.
        raw_decision = get_ai_response(chat_history=history, user_memory=long_term_memory)

        # 5) Save assistant message so future turns include model output.
        save_message(user_id=request.user_id, role="assistant", content=raw_decision)

        decision = json.loads(_clean_json_text(raw_decision))

        action = decision.get("action")
        params = decision.get("params", {})

        if not isinstance(action, str):
            raise HTTPException(status_code=502, detail="LLM returned invalid action format.")
        if not isinstance(params, dict):
            raise HTTPException(status_code=502, detail="LLM returned invalid params format.")

        result = execute_action(action=action, params=params)
        return {"result": result}
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail="LLM did not return valid JSON.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to process chat request: {str(exc)}",
        )