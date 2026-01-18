from sqlalchemy.orm import Session
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserPatch
from app.core.exceptions import NotFoundException

def create_user(db: Session, user: UserCreate):
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def list_users(db: Session):
    return db.query(User).all()

def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    return user

def update_user_put(db: Session, user_id: int, user_data: UserUpdate):
    user = get_user(db, user_id)
    for field, value in user_data.dict().items():
        setattr(user, field, value)
    db.commit()
    return user

def update_user_patch(db: Session, user_id: int, user_data: UserPatch):
    user = get_user(db, user_id)
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    return user

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()
