# Внешние зависимости
from fastapi import APIRouter
# Внутренние модули
from web_app.src.routers.html_router import router as html_router
from web_app.src.routers.auth_router import router as auth_router
from web_app.src.routers.event_router import router as event_router
from web_app.src.routers.user_router import router as user_router


router = APIRouter()
router.include_router(html_router)
router.include_router(auth_router)
router.include_router(event_router)
router.include_router(user_router)