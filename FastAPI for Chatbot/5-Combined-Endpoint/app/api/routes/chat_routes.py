from fastapi import APIRouter
from fastapi import Query
from app.schemas.chat_schema import ChatRequest

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/{conversation_id}")
def chat_endpoint(conversation_id: str, request: ChatRequest, tempreture: float =Query(0.3, ge=0, le=1), tone: str = Query(None)):
    final_temperature = tempreture if tempreture is not None else request.temperature
    final_tone = tone if tone is not None else request.tone
    return {
        "conversation_id": conversation_id,
        "user_id": request.user_id,
        "message": request.message,
        "temperature": final_temperature,
        "tone": final_tone,
        "Info": "This is a combined endpoint that accepts both path parameters and query parameters, along with a request body."}