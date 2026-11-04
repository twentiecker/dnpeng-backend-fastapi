from fastapi import APIRouter
from app.features.auth import router as auth
from app.features.users import router as users
from app.features.pkrt import router as pkrt
from app.features.pkp import router as pkp
from app.features.pmtb import router as pmtb
from app.features.eksim import router as eksim
from app.features.pdb import router as pdb
from app.features.files import router as files
from app.features.monitoring import router as monitoring
from app.features.comments import router as comments
from app.features.projects import router as projects
from app.features.master_wilayah import router as master_wilayah

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(pkrt.router, prefix="/pkrt", tags=["PKRT"])
api_router.include_router(pkp.router, prefix="/pkp", tags=["PKP"])
api_router.include_router(pmtb.router, prefix="/pmtb", tags=["PMTB"])
api_router.include_router(eksim.router, prefix="/eksim", tags=["Eksim"])
api_router.include_router(pdb.router, prefix="/pdb", tags=["PDB"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
api_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(
    master_wilayah.router, prefix="/master-wilayah", tags=["Master Wilayah"]
)
