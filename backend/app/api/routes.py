from fastapi import APIRouter
from backend.app.api.overview import router as overview_router
from backend.app.api.tokens import router as tokens_router
from backend.app.api.usage import router as usage_router
from backend.app.api.tools import router as tools_router
from backend.app.api.errors import router as errors_router
from backend.app.api.users import router as users_router
from backend.app.api.predictions import router as predictions_router

router = APIRouter()

router.include_router(overview_router)
router.include_router(tokens_router)
router.include_router(usage_router)
router.include_router(tools_router)
router.include_router(errors_router)
router.include_router(users_router)
router.include_router(predictions_router)