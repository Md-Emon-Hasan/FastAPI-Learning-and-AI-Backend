from typing import List, Dict
from app.schemas.user import UserCreate
from app.core.exceptions import NotFoundException

def create_user(db: List[Dict], user: UserCreate) -> Dict:
    user_id = len(db) + 1

    new_user = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age
    }

    db.append(new_user)
    return new_user


def list_users(db: List[Dict]) -> List[Dict]:
    return db


def get_user_by_id(db: List[Dict], user_id: int) -> Dict:
    for user in db:
        if user["id"] == user_id:
            return user

    raise NotFoundException(
        message="User not found",
        details={"user_id": user_id}
    )
