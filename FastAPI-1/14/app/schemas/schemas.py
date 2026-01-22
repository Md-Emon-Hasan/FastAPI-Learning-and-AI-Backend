from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ============= User Schemas =============

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    API_CLIENT = "api_client"

class UserCreate(BaseModel):
    """User registration input"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """User login input"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User data যা API response এ return করবো"""
    id: int
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"

# ============= Conversation Schemas =============

class MessageCreate(BaseModel):
    """User এর message input"""
    content: str = Field(..., min_length=1)

class MessageResponse(BaseModel):
    """Message response"""
    id: int
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ConversationCreate(BaseModel):
    """New conversation তৈরি করার input"""
    title: Optional[str] = None
    system_prompt: Optional[str] = None

class ConversationResponse(BaseModel):
    """Conversation info"""
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    message_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class ConversationWithMessages(ConversationResponse):
    """Conversation সহ সব messages"""
    messages: List[MessageResponse] = []

class ChatRequest(BaseModel):
    """Chat endpoint এর input"""
    message: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None
    stream: bool = False
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class ChatResponse(BaseModel):
    """Chat endpoint এর response"""
    conversation_id: int
    message: MessageResponse
    assistant_message: MessageResponse

# ============= Document Schemas =============

class DocumentUpload(BaseModel):
    """Document upload করার পরে response"""
    id: int
    filename: str
    file_size: int
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    """Document details"""
    id: int
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    created_at: datetime
    processed_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

# ============= Agent Schemas =============

class AgentRunRequest(BaseModel):
    """Agent execution এর input"""
    task: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = {}
    max_iterations: int = Field(default=5, ge=1, le=20)

class AgentRunResponse(BaseModel):
    """Agent execution result"""
    task_id: str
    status: str  # running, completed, failed
    result: Optional[str] = None
    steps: List[Dict[str, Any]] = []
    
# ============= Error Schema =============

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None