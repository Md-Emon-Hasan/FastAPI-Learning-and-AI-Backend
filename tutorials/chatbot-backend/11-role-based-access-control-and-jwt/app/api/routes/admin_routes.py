from fastapi import APIRouter
from fastapi import Depends
from app.core.security import require_admin
from app.schemas.response_schema import APIResponse
from app.db.models import User

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get('/dashboard', response_model=APIResponse)
def admin_dashboard(admin_user: User = Depends(require_admin)):
    return APIResponse(
        status="success",
        data={
            "message": f"Welcome to the admin dashboard, {admin_user.email}!"
        }
    )