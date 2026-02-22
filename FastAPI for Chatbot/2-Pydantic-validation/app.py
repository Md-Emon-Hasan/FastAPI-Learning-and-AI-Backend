from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import Field
from typing import Optional

app = FastAPI(title="Pydantic Validation Example")

# First Example: Basic Validation
# class ChatRequest(BaseModel):
#     user_id : int
#     message : str

# @app.post("/chat")
# def chat(request: ChatRequest):
#     return {"msg": "Valid request received"}


# Second Example: Validation Rules
# class ChatRequest(BaseModel):
#     user_id : str = Field(..., min_length=5, max_length=20, description="User ID must be between 5 and 20 characters")
#     message : str = Field(..., min_length=1, max_length=200, description="Message must be between 1 and 200 characters")

# @app.post("/chat")
# def chat(request: ChatRequest):
#     return {"msg": "valid request received"}


# Third Example: Optional Fields
# class ChatRequest(BaseModel):
#     user_id : str
#     message : str
#     tone : Optional[str] = None
    
# @app.post("/chat")
# def chat(request: ChatRequest):
#     return {'message': "Request received with tone"}


# Fourth Example: Default Values
# class ChatRequest(BaseModel):
#     user_id : str
#     message : str
#     tempreture : float = 0.3
    
# @app.post('/chat')
# def chat(request: ChatRequest):
#     return {"message":"Request received with default temperature"}


# Fifth Example: Real Chatbot Style Validation Model
class ChatRequest(BaseModel):
    user_id : str = Field(..., min_length=5, max_length=20, description="User ID must be between 5 and 20 characters")
    message : str = Field(..., min_length=1, max_length=200, description="Message must be between 1 and 200 characters")
    tone : Optional[str] = Field(None, description="Optional tone for the response")
    temperature : float = Field(0.3, ge=0.0, le=1.0, description="Temperature for response generation (0.0 to 1.0)")
    
@app.post("/chat")
def chat(request: ChatRequest):
    return {'message': "Request received with all validations"}