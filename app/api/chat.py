from fastapi import APIRouter

from app.schema.chat_schema import ChatRequest
from app.services.chat_service import chat_service


router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest):

    response = chat_service.process_message(
        request.session_id,
        request.message
    )


    return {
        "response": response
    }