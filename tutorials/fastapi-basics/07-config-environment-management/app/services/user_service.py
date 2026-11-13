from typing import List, Dict
from app.schemas.user import UserCreate


def create_user(db: List[Dict], user: UserCreate) -> Dict:
    user_id = len(db) + 1

    new_user = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
    }

    db.append(new_user)
    return new_user

def list_users(db: List[Dict]) -> List[Dict]:
    return db
