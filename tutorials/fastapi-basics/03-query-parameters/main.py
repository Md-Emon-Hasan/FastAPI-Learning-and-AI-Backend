from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.get('/list_users')
def read_users(
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = None
):
    return {'limit' : limit,
            'skip' : skip,
            'search' : search}