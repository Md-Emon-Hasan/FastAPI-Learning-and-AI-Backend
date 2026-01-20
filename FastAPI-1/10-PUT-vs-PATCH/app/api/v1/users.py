from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.models.user import User
from app.schemas.user import (
    UserCreate,
    UserPut,
    UserPatch,
    UserResponse
)
from app.dependencies.common import get_db

router = APIRouter(prefix="/users", tags=["Users"])

# CREATE
@router.post("", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        name=user.name,
        email=user.email,
        age=user.age
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# READ ALL
@router.get("", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# PUT — FULL REPLACE
@router.put("/{user_id}", response_model=UserResponse)
def update_user_put(
    user_id: int,
    user: UserPut,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(404, "User not found")

    # FULL replace
    db_user.name = user.name
    db_user.email = user.email
    db_user.age = user.age

    db.commit()
    return db_user


# PATCH — PARTIAL UPDATE
@router.patch("/{user_id}", response_model=UserResponse)
def update_user_patch(
    user_id: int,
    user: UserPatch,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(404, "User not found")

    # Only update provided fields
    if user.name is not None:
        db_user.name = user.name
    if user.email is not None:
        db_user.email = user.email
    if user.age is not None:
        db_user.age = user.age

    db.commit()
    return db_user
