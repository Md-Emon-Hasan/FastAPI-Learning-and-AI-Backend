from fastapi import FastAPI

app = FastAPI()

@app.get('/users')
def read_users():
    return {'name' : 'Emon Hasan'}

@app.get('/users/{user_id}')
def read_user_id(user_id: int):
    return {'user_id' : user_id,
            'name' : 'Emon Hasan'}