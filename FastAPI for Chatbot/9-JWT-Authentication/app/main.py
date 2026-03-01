from fastapi import FastAPI
from app.db.database import Base
from app.db.database import engine
from app.api.routes.auth_routes import router as auth_router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="JWT Authentication API")
app.include_router(auth_router)