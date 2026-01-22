# from pydantic import BaseModel, Field
# from typing import List, Optional
# from datetime import datetime

# class ChatMessage(BaseModel):
#     role: str = Field(..., description="user or assistant")
#     content: str

# class ChatRequest(BaseModel):
#     message: str = Field(..., min_length=1, max_length=5000)
#     conversation_id: Optional[str] = None
#     temperature: float = Field(default=0.7, ge=0, le=2)
#     max_tokens: int = Field(default=1024, ge=1, le=4096)

# class ChatResponse(BaseModel):
#     conversation_id: str
#     message: str
#     tokens_used: int
#     timestamp: datetime

# class ConversationHistory(BaseModel):
#     conversation_id: str
#     messages: List[ChatMessage]
#     created_at: datetime
#     updated_at: datetime

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, ge=1, le=4096)

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    tokens_used: int
    timestamp: datetime

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime