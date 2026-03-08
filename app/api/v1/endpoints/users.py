from fastapi import APIRouter, Depends
from app.api.deps import require_role
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/admin-only")
def admin_data(user=Depends(require_role("admin"))):
    return {"message": "Welcome Admin"}


@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }
