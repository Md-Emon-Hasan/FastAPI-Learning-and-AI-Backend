# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from datetime import datetime

# class UserCreate(BaseModel):
#     email: EmailStr
#     password: str = Field(..., min_length=8)
#     full_name: Optional[str] = None

# class UserResponse(BaseModel):
#     id: int
#     email: EmailStr
#     full_name: Optional[str]
#     is_active: bool
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

# class Token(BaseModel):
#     access_token: str
#     token_type: str = "bearer"

# class TokenData(BaseModel):
#     user_id: Optional[int] = None


from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None