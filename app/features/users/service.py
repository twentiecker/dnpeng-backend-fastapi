from sqlalchemy.orm import Session
from app.features.users.repository import get_users_role


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
