from fastapi import FastAPI, HTTPException
from .schemas import ChatRequest
from .ai_engine.langchain_agent import run_agent

app = FastAPI()

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        result = run_agent(user_message=request.message)
        return {"result": result}
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to process chat request: {str(exc)}",
        )