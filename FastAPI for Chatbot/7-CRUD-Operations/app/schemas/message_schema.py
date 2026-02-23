from pydantic import BaseModel
from pydantic import Field

class MessageCreate(BaseModel):
    user_id : str = Field(..., description="ID of the user sending the message")
    content : str = Field(..., description="content of the message")
    
class MessageUpdate(BaseModel):
    content: str = Field(..., description="Updated content of the message")
    
class MessageResponse(BaseModel):
    id: str = Field(..., description="ID of the message")
    user_id: str = Field(..., description="ID of the user who sent the message")
    content: str = Field(..., description="Content of the message")