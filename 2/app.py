from fastapi import FastAPI
import json

app = FastAPI()

def load_data():
    with open('paitents.json','r') as f:
        data = json.load(f)
    return data

@app.get('/')
def hello():
    return {'messages':'hello world'}

@app.get('/about')
def about():
    return {'messages':'A fully finctional app to manage your paitents records'}

@app.get('/view')
def view():
    data = load_data()
    return data