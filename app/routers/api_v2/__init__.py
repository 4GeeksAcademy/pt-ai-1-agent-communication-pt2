from fastapi import APIRouter

from app.routers.api_v2.creators import router as creators_router
from app.routers.api_v2.franchises import router as franchises_router
from app.routers.api_v2.genres import router as genres_router
from app.routers.api_v2.media_items import router as media_items_router
from app.routers.api_v2.media_types import router as media_types_router

router = APIRouter(prefix="/api/v2")
router.include_router(media_items_router)
router.include_router(creators_router)
router.include_router(franchises_router)
router.include_router(media_types_router)
router.include_router(genres_router)
