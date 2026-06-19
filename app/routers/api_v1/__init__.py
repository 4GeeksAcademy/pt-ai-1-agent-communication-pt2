from fastapi import APIRouter

from app.routers.api_v1.media_items import router as media_items_router

router = APIRouter(prefix="/api/v1")
router.include_router(media_items_router)
