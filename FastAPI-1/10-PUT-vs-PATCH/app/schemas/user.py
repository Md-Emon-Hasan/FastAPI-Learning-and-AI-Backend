from pydantic import BaseModel, EmailStr
from typing import Optional

# POST
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int

# PUT → FULL replace (সব required)
class UserPut(BaseModel):
    name: str
    email: EmailStr
    age: int

# PATCH → PARTIAL update (সব optional)
class UserPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True
