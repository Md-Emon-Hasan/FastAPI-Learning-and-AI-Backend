from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth_schema import RegisterRequest
from app.schemas.response_schema import APIResponse
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


# Register (JSON body)
@router.post("/register", response_model=APIResponse)
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = auth_service.register_user(
        db,
        email=request.email,
        password=request.password
    )

    if not user:
        raise HTTPException(status_code=400, detail="User already exists")

    return APIResponse(
        status="success",
        data={"user_id": user.id},
        error=None
    )


# Login (OAuth2 form - Swagger compatible)
@router.post("/login", response_model=APIResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service)
):

    user = service.authenticate_user(
        db,
        email=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = service.generate_token(user)

    return APIResponse(
        status="success",
        data={
            "access_token": token,
            "token_type": "bearer"
        },
        error=None
    )