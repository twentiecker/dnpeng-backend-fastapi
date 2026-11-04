from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session
from app.core.security import verify_password, hash_password
from app.models.user import User
from app.features.users.repository import (
    get_users_role,
    update_password,
    search_users,
)
from app.features.users.schema import ChangePasswordRequest
import re


def get_users_by_role(role: str, db: Session):
    users = get_users_role(role, db)

    enriched_users = []

    for user in users:
        enriched_users.append(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at,
            }
        )

    # sort descending (terbaru dulu)
    sorted_users = sorted(enriched_users, key=lambda x: x["created_at"], reverse=True)

    # ✅ baru format setelah sorting
    result = []
    for user in sorted_users:
        result.append(
            {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "date": user["created_at"].strftime("%d %b %Y"),
            }
        )

    return result


def validate_password_strength(password: str):
    """
    Password minimal:
    - 8 karakter
    - 1 huruf besar
    - 1 huruf kecil
    - 1 angka
    - 1 simbol
    """

    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password minimal 8 karakter.",
        )

    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password harus mengandung huruf besar.",
        )

    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password harus mengandung huruf kecil.",
        )

    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=400,
            detail="Password harus mengandung angka.",
        )

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\]]", password):
        raise HTTPException(
            status_code=400,
            detail="Password harus mengandung simbol.",
        )


def change_password(
    payload: ChangePasswordRequest,
    current_user: User,
    db: Session,
):
    # 1. cek password lama
    if not verify_password(
        payload.old_password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=400,
            detail="Password lama salah.",
        )

    # 2. konfirmasi password
    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Konfirmasi password tidak sesuai.",
        )

    # 3. password baru tidak boleh sama
    if verify_password(
        payload.new_password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=400,
            detail="Password baru tidak boleh sama dengan password lama.",
        )

    # 4. cek strength password
    # validate_password_strength(payload.new_password)

    # 5. hash password baru
    hashed_password = hash_password(payload.new_password)

    # 6. simpan
    update_password(
        current_user,
        hashed_password,
        db,
    )

    return {"message": "Password berhasil diperbarui."}


def search_users_service(
    db: Session,
    keyword: str,
):
    keyword = keyword.strip()

    if not keyword:
        return []

    return search_users(
        db=db,
        keyword=keyword,
    )
