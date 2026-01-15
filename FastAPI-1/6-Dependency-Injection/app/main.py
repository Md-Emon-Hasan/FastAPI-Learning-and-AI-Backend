from fastapi import FastAPI
from app.api.users import router as user_router

app = FastAPI(
    title="FastAPI DI Example",
    version="1.0.0"
)

app.include_router(user_router)

@app.get("/")
def health_check():
    return {"status": "ok"}
