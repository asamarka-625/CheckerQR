# Внешние зависимости
from typing import Annotated, Dict, List
from pydantic import Field
from fastapi import APIRouter, Depends
# Внутренние модули
from models import User
from web_app.src.dependencies import (get_current_user_by_access_token, get_data_by_refresh_token,
                                      verify_csrf_token)
from web_app.src.crud import sql_get_users_by_name
from web_app.src.utils import ensure_user_access
from web_app.src.schemas import UserScheme


router = APIRouter(
    prefix="/api/v1/user",
    tags=["API"]
)


@router.get(
    path="/search/{name}",
    response_model=List[UserScheme],
    summary="Поиск пользователей"
)
async def create_event(
    name: Annotated[str, Field(max_length=128)],
    current_user: User = Depends(get_current_user_by_access_token),
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token),
    csrf_user_id: str = Depends(verify_csrf_token)
):
    ensure_user_access(
        user=current_user,
        token_data=token_data,
        user_id=csrf_user_id
    )

    return await sql_get_users_by_name(
        name=name
    )