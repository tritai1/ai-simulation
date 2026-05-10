from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    role: str
    session_id: str