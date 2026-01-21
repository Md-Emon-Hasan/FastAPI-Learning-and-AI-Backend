from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.token import Token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup")
def signup(email: str, password: str, role: str = "user", db: Session = Depends(get_db)):
    if role not in ["user", "admin"]:
        raise HTTPException(400, "Role must be user or admin")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "User already exists")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()

    return {"message": "User created", "role": role}


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    access_token = create_access_token({
        "sub": user.email,
        "role": user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
