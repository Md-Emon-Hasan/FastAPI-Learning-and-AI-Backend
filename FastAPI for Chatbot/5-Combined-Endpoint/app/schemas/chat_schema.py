from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=1, max_length=2000)
    temperature: float = Field(0.3, ge=0, le=1)
    tone: Optional[str] = "neutral"