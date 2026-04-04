from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    user_id: str = Field(..., max_length=256)
    message: str = Field(..., min_length=1, max_length=32000)

    @field_validator("user_id")
    @classmethod
    def user_id_stripped(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("user_id must not be empty")
        return s


class ChatResponse(BaseModel):
    result: str
    tool_used: str | None = None
    tool_result: object | None = None
