from fastapi import FastAPI
from app.api.routes.chat_routes import router as chat_router

app = FastAPI(title="Chatbot API with Combined Endpoint")

app.include_router(chat_router)