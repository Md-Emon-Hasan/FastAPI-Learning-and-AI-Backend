from fastapi import FastAPI, HTTPException

app = FastAPI()

# Fake DB
users_db = {
    1: {"name": "user1", "age": 22},
    2: {"name": "user2", "age": 25},
}

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    del users_db[user_id]
