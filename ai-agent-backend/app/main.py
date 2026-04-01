from fastapi import FastAPI, HTTPException
from openai import APIError, APIStatusError, AuthenticationError, RateLimitError
from .schemas import ChatRequest
from .llm import get_ai_response

app = FastAPI()

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        reply = get_ai_response(request.message)
        return {"response": reply}
    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="OpenAI quota/rate limit reached. Check billing or try again later.",
        )
    except AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Invalid OpenAI API key. Check OPENAI_API_KEY in .env.",
        )
    except APIStatusError as exc:
        # Surface upstream API status while keeping a predictable response shape.
        raise HTTPException(
            status_code=502,
            detail=f"Upstream OpenAI error: {exc.status_code}",
        )
    except APIError:
        raise HTTPException(
            status_code=502,
            detail="OpenAI API request failed.",
        )