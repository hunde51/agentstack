from fastapi import FastAPI
from .schemas import ChatRequest
from .llm import get_ai_response

app = FastAPI()

@app.post("/chat")
def chat(request: ChatRequest):
    reply = get_ai_response(request.message)
    return {"response": reply}