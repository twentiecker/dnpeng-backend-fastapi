from fastapi import (
    FastAPI,
    Request,
    status,
    HTTPException,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import logging
import time
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import validation_exception_handler
from app.core.static import setup_static
from app.db.init_db import seed_superadmin

logger = logging.getLogger(__name__)


# -----------------------------
# Security Headers Middleware
# -----------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response


# -----------------------------
# Request Logging Middleware
# -----------------------------
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()

        response = await call_next(request)

        process_time = time.time() - start
        logger.info(
            f"{request.method} {request.url.path} "
            f"{response.status_code} "
            f"{process_time:.3f}s"
        )

        return response


# -----------------------------
# Lifespan Event
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("FastAPI application starting")
    seed_superadmin()
    yield
    logging.info("FastAPI application shutting down")


# -----------------------------
# Create App
# -----------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    # -----------------------------
    # comment root_path saat deploy di cpanel,
    # isi dengan nama sub_direktori yang digunakan
    # untuk deploy fastapi dengan python app
    # -----------------------------
    # root_path="/<sub_directory_name>",
)


# -----------------------------
# Static Files (Public Assets)
# -----------------------------
setup_static(app)


# -----------------------------
# Middleware
# -----------------------------

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# gzip compression (lebih cepat untuk frontend)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# security headers
app.add_middleware(SecurityHeadersMiddleware)

# request logging
app.add_middleware(LoggingMiddleware)

# trusted host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # production isi domain saja
)


# -----------------------------
# Router
# -----------------------------
app.include_router(api_router, prefix="/api/v1")


# -----------------------------
# Logging Config
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


# -----------------------------
# Validation Exception Handler (spesifik)
# -----------------------------
app.add_exception_handler(RequestValidationError, validation_exception_handler)


# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"success": False, "message": exc.detail},
#     )


# -----------------------------
# Global Exception Handler (fallback)
# -----------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "Internal Server Error"},
    )


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    return {"message": "FastAPI Backend Running"}
