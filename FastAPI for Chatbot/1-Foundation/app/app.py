from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"Message":"Hello, World!"}

@app.get("/status")
def status():
    return {"Status":"Server is running smoothly!"}

@app.get("/hello")
def say_hello():
    return {'Message': 'Hello Backend Developer!'}

@app.get("/user/{user_id}")
def get_user(user_id: int):
    return {"User ID": user_id}

