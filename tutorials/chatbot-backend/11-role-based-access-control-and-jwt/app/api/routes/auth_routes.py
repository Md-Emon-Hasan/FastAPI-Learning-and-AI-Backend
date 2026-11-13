from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


from app.db.database import get_db
from app.schemas.response_schema import APIResponse
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


# Register (JSON body)
@router.post("/register", response_model=APIResponse)
def register(
    email: str,
    password: str,
    role: str = "user",
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service)
):
    user = service.register_user(db, email, password, role)

    if not user:
        raise HTTPException(status_code=400, detail="User already exists")

    return APIResponse(
        status="success",
        data={"user_id": user.id,
        "role": user.role}
    )


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service)
):
    user = service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = service.generate_token(user)

    # Swagger OAuth2 expects EXACT shape
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }