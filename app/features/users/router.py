from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.api.deps import get_db, get_current_user, require_role
from app.features.users.service import get_users_by_role

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


@router.get("/{role}")
def get_user(
    role: str,
    db: Session = Depends(get_db),
):
    return get_users_by_role(role, db)
