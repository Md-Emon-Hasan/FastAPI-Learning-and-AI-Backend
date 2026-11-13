from fastapi import FastAPI
from app.api.routes.chat_routes import router as chat_router

app = FastAPI(title="Chatbot API with Validation", description="A simple chatbot API with request validation using Pydantic models.", version="1.0.0")

app.include_router(chat_router)