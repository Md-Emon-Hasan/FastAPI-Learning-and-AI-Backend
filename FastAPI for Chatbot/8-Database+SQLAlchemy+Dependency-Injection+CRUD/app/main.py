from fastapi import FastAPI
from app.db.database import engine, Base
from app.api.routes.message_routes import router as message_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SQLite CRUD API")

app.include_router(message_router)