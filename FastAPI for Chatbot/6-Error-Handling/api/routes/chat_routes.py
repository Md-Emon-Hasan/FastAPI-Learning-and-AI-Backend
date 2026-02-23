from fastapi import APIRouter
from fastapi import Query
from fastapi import HTTPException
from schemas.chat_schema import ChatRequest
from schemas.response_schema import APIResponse

router = APIRouter(prefix="/chat", tags=['Chat'])

@router.post("/{conversation_id}", response_model=APIResponse)
def chat_endpoint(
    conversation_id : str,
    request : ChatRequest,
    temperature : float = Query(None, ge=0.0, le=1.0, description="Temperature for response generation (0.0 to 1.0)"),
    tone : str = Query(None)
):
    if request.message.lower() == "error":
        raise HTTPException(status_code=400, detail="Invalid message content")
    
    if len(conversation_id) < 3:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    final_temperature = temperature if temperature is not None else request.temperature
    final_tone = tone if tone is not None else request.tone

    result = {
        "conversation_id": conversation_id,
        "user_id": request.user_id,
        "message": request.message,
        "temperature": final_temperature,
        "tone": final_tone
    }
    
    return APIResponse(
        status="success",
        data=result,
        error=None
    )