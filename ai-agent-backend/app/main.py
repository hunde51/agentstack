import json
from fastapi import FastAPI, HTTPException
from .schemas import ChatRequest
from .llm import get_ai_response

app = FastAPI()


def get_weather(city: str):
    # Mock weather data for now; this can be replaced with a real API call later.
    return {"city": city, "forecast": "sunny", "temperature_c": 24}


def get_users():
    # Mock user list for demonstration.
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ]


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
        raw_decision = get_ai_response(request.message)
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