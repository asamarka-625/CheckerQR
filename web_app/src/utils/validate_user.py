# Внешние зависимости
from typing import Dict
from uuid import UUID
from fastapi import HTTPException, status
# Внутренние модули
from models import User
from web_app.src.utils.init_redis import redis_service


# Вспомогательная функция для валидации токенов пользователя
def ensure_user_access(
    user: User,
    token_data: Dict[str, str],
    user_id: str
):
    if not (str(user.id) == token_data["user_id"] == user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token user mismatch"
        )

async def ensure_user_event_access(
    event_id: UUID,
    user_id: int,
    only_owner: bool = False
):
    if not await redis_service.check_event_access(
        event_id=str(event_id),
        user_id=user_id,
        only_owner=only_owner
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав"
        )