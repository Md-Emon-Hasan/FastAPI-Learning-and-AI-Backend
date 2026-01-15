from fastapi import FastAPI, status
from app.schemas.user import UserCreate, UserResponse

app = FastAPI()

@app.post('/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user : UserCreate):
    fake_user = {
        'id' : 1,
        'name' : user.name,
        'email' : user.email,
        'age' : user.age
    }
    return fake_user