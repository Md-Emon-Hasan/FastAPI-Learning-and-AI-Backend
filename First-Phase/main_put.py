from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# In-memory fake database
users_db = {
    1: {"name": "user1", "age": 22},
    2: {"name": "user2", "age": 25},
}

class UserCreate(BaseModel):
    name: str
    age: int

@app.get("/")
def check_health():
    return {"status": "ok"}

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    new_id = max(users_db.keys(), default=0) + 1
    users_db[new_id] = user.dict()
    return {"id": new_id, "user": users_db[new_id]}

# PUT = full update
@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate):
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Full replace
    users_db[user_id] = {
        "name": user.name,
        "age": user.age
    }

    return {
        "id": user_id,
        "user": users_db[user_id],
        "message": "User updated successfully"
    }


# for bowser show
@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user_id,
        "user": users_db[user_id]
    }
