import csv
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


def seed_multiple_superadmin():
    db = SessionLocal()

    users = [
        {
            "name": "Lukman",
            "email": "arifandhi@bps.go.id",
            "password": "NHAgustina@55874",
            "role": "admin",
        },
        {
            "name": "Nur Hafizah",
            "email": "nhagustina@bps.go.id",
            "password": "jaya5ada",
            "role": "admin",
        },
    ]

    for u in users:
        existing_user = db.query(User).filter(User.email == u["email"]).first()
        if not existing_user:
            new_user = User(
                name=u["name"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            )
            db.add(new_user)

    db.commit()
    db.close()


def seed_multiple_users():
    db = SessionLocal()

    users = []

    with open("app/db/users.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=",")

        for row in reader:
            users.append(
                {
                    "name": row["name"],
                    "email": row["email"],
                    "password": "Bps123",
                    "role": row["role"],
                }
            )

    for u in users:
        existing_user = db.query(User).filter(User.email == u["email"]).first()
        if not existing_user:
            new_user = User(
                name=u["name"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            )
            db.add(new_user)

    db.commit()
    db.close()
