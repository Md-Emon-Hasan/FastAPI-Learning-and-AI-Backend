from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# In-memory fake database
users_db = {
    1: {"name": "user1", "age": 22},
    2: {"name": "user2", "age": 25},
}

# Request body schema
class UserCreate(BaseModel):
    name: str
    age: int

# Health check
@app.get("/")
def check_health():
    return {"status": "ok"}

# Create user (POST only)
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    # Duplicate name check (basic validation)
    for existing_user in users_db.values():
        if existing_user["name"] == user.name:
            raise HTTPException(
                status_code=400,
                detail="User with this name already exists"
            )

    new_id = max(users_db.keys(), default=0) + 1

    users_db[new_id] = {
        "name": user.name,
        "age": user.age
    }

    return {
        "id": new_id,
        "user": users_db[new_id],
        "message": "User created successfully"
    }
