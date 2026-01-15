from app.schemas.user import UserCreate
from fastapi import FastAPI

app = FastAPI()

@app.post('/users')
def create_user(user: UserCreate):
    return {
        'message' : 'User created successfully',
        'user' : user
    }