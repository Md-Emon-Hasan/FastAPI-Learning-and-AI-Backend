from fastapi import FastAPI

app = FastAPI(
    title = 'First API',
    description = 'This is my first API using FastAPI framework',
    version = '1.0.0'
)

@app.get('/')
def root():
    return {'message':'hello world'}