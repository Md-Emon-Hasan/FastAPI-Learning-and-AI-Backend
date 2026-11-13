from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest

router = APIRouter(prefix="/chat", tags=['Chat'])

@router.post("/")
def chat_endpoint(request: ChatRequest):
    return{
        "user_id": request.user_id,
        "message": request.message,
        "temperature": request.temperature,
        "tone": request.tone,
        'status' : 'Message received successfully'
    }