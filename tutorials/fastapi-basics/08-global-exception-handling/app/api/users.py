from fastapi import APIRouter, Depends, status
from typing import List

from app.schemas.user import UserCreate, UserResponse
from app.dependencies.common import get_db
from app.services.user_service import (
    create_user,
    list_users,
    get_user_by_id
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user_api(
    user: UserCreate,
    db = Depends(get_db)
):
    return create_user(db, user)


@router.get(
    "",
    response_model=List[UserResponse]
)
def list_users_api(
    db = Depends(get_db)
):
    return list_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user_api(
    user_id: int,
    db = Depends(get_db)
):
    return get_user_by_id(db, user_id)
