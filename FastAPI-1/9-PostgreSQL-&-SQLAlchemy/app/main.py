from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.api.v1.users import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users_router)
