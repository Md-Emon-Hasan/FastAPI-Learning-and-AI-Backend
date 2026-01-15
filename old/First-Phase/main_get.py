from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# In-memory fake database
users_db = {
    1: {"name": "user1", "age": 22},
    2: {"name": "user2", "age": 25},
}

@app.get('/')
def check_health():
    return {'status': 'ok'}

@app.get('/users')
def get_users():
    return {'users_db' : users_db}