from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from enum import Enum

app = FastAPI(title="Pydantic Validation Demo")

# ----------------------------
# Fake in-memory database
# ----------------------------
users_db = {
    1: {"name": "Alice", "age": 25, "email": "alice@gmail.com", "role": "user"},
    2: {"name": "Bob", "age": 30, "email": "bob@gmail.com", "role": "admin"},
}


# ----------------------------
# Enum Validation
# ----------------------------
class Role(str, Enum):
    admin = "admin"
    user = "user"


# ----------------------------
# Create User Schema
# ----------------------------
class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=20)
    age: int = Field(..., ge=18, le=100)
    email: EmailStr
    role: Role

    # Custom validation (business rule)
    @field_validator("name")
    @classmethod
    def name_must_be_alpha(cls, v):
        if not v.isalpha():
            raise ValueError("Name must contain only letters")
        return v


# ----------------------------
# Partial Update Schema (PATCH)
# ----------------------------
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    age: Optional[int] = Field(None, ge=18)
    role: Optional[Role] = None


# ----------------------------
# Response Schema
# ----------------------------
class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    email: EmailStr
    role: Role


# ----------------------------
# Health Check
# ----------------------------
@app.get("/")
def health_check():
    return {"status": "API is running"}


# ----------------------------
# GET (Read all)
# ----------------------------
@app.get("/users")
def get_users(
    limit: int = Query(10, gt=0),
    active: bool = Query(True)
):
    return {"limit": limit, "active": active, "data": users_db}


# ----------------------------
# GET (Read one)
# ----------------------------
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int = Path(..., gt=0)):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": user_id, **user}


# ----------------------------
# POST (Create)
# ----------------------------
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    new_id = max(users_db.keys()) + 1
    users_db[new_id] = user.dict()
    return {"message": "User created", "id": new_id}


# ----------------------------
# PUT (Full update)
# ----------------------------
@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    users_db[user_id] = user.dict()
    return {"message": "User fully updated"}


# ----------------------------
# PATCH (Partial update)
# ----------------------------
@app.patch("/users/{user_id}")
def patch_user(user_id: int, user: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.dict(exclude_unset=True).items():
        users_db[user_id][key] = value

    return {"message": "User partially updated"}


# ----------------------------
# DELETE
# ----------------------------
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    del users_db[user_id]
    return {"message": "User deleted"}
