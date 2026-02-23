from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    user_id : str = Field(..., min_length=2, max_length=50)
    message : str = Field(..., min_length=1, max_length=500)
    temperature : Optional[str] = 'neutral'
    