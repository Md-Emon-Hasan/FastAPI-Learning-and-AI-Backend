from fastapi import FastAPI
from app.db.database import Base
from app.db.database import engine
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.user_routes import router as user_router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="JWT Protection with FastAPI")

app.include_router(auth_router)
app.include_router(user_router)