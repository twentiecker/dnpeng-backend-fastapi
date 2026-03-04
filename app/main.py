from fastapi import FastAPI, Request
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import seed_superadmin
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from fastapi.responses import JSONResponse


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response


app = FastAPI(title=settings.APP_NAME)

app.include_router(api_router, prefix="/api/v1")
app.add_middleware(SecurityHeadersMiddleware)

seed_superadmin()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


@app.get("/")
def root():
    return {"message": "FastAPI Backend Running"}
