from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def health_check():
    return {'status':'ok'}

@app.get('/users')
def get_users():
    return {'users': ['user1', 'user2', 'user3']}

@app.get('/users/{user_id}')
def get_user(user_id: int):
    return {'user_id' : user_id}