from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Fake DB
users_db = {
    1: {"name": "user1", "age": 22},
    2: {"name": "user2", "age": 25},
}

# Partial update schema
class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

@app.patch("/users/{user_id}")
def patch_user(user_id: int, user: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    # Only update provided fields
    if user.name is not None:
        users_db[user_id]["name"] = user.name

    if user.age is not None:
        users_db[user_id]["age"] = user.age

    return {
        "id": user_id,
        "user": users_db[user_id],
        "message": "User partially updated"
    }
