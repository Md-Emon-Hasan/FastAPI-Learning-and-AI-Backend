from sqlalchemy.orm import Session
from app.db.models import User
from app.core.security import hash_password, verify_password, create_access_token

class AuthService:

    def register_user(self, db: Session, email: str, password: str):
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return None

        user = User(
            email=email,
            hashed_password=hash_password(password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)   # 🔥 FIXED: instance refresh, not class
        return user

    def authenticate_user(self, db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def generate_token(self, user: User):
        return create_access_token({"sub": str(user.id)})

def get_auth_service():
    return AuthService()