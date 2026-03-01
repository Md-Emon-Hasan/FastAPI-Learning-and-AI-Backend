from fastapi import APIRouter
from fastapi import Depends
from app.core.security import get_current_user
from app.schemas.response_schema import APIResponse
from app.db.models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get('/me', response_model=APIResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return APIResponse(
        status="success",
        data={
            "id":current_user.id,
            "username":current_user.email,
            "role":current_user.role
        }
    )