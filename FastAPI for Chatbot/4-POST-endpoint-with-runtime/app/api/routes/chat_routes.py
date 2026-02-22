from fastapi import APIRouter
from fastapi import Query
from app.schemas.chat_schema import ChatRequest

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/")
def chat_endpoint(
    request: ChatRequest,
    temperature: float = Query(0.3, ge=0, le=1, description="Controls the randomness of the response, between 0 and 1"),
    tone: str = Query("neutral", description="The tone of the response, e.g., 'friendly', 'formal', 'neutral'")):
    
    final_temperature = temperature if temperature is not None else request.temperature
    final_tone = tone if tone is not None else request.tone
    
    return {
        "user_id": request.user_id,
        "message": request.message,
        "temperature": final_temperature,
        "tone": final_tone,
        "info" : "This endpoint processes the chat message with the specified temperature and tone."
    }
