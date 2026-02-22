from pydantic import BaseModel
from pydantic import Field
from typing import Optional

class ChatRequest(BaseModel):
    user_id : str = Field(..., min_length=1, max_length=50, description="Unique identifier for the user")
    message : str = Field(..., min_length=1, max_length=500, description="The message sent by the user")
    temperature : float = Field(0.5, ge=0.0, le=1.0, description="Controls the randomness of the response, between 0 and 1")
    tone : Optional[str] = "neutral"