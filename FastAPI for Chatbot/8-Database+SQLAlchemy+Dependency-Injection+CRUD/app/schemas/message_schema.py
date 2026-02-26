from pydantic import BaseModel
from pydantic import Field

class MessageCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    content: str = Field(..., min_length=1, max_length=500)
    
class MessageUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)
    
class MessageOut(BaseModel):
    id: int
    user_id: int
    content: str
    
    class Config:
        from_attributes = True