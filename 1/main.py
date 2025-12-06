from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def hello():
    return {'messages':'hello world'}

@app.get('/about')
def about():
    return {'messages':'this is my messages'}