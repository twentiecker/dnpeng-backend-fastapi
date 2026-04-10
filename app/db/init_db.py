from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def seed_superadmin():
    db = SessionLocal()
    if not db.query(User).filter(User.email == "admin@admin.com").first():
        admin = User(
            name="Admin",
            email="admin@admin.com",
            hashed_password=hash_password("admin123"),
            role="admin",
        )
        db.add(admin)
        db.commit()
    db.close()
