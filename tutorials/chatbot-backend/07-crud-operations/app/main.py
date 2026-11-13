from fastapi import FastAPI
from app.api.routes.message_routes import router as message_router

app = FastAPI(title="Chatbot API with CRUD Operations")

app.include_router(message_router)