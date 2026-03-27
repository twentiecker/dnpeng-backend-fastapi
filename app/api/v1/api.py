from fastapi import APIRouter
from app.features.auth import router as auth
from app.features.users import router as user
from app.features.pkrt import router as pkrt
from app.features.files import router as files

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(pkrt.router, prefix="/pkrt", tags=["PKRT"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
