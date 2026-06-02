# Внешние зависимости
from typing import Dict
from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
# Внутренние модули
from models import User
from web_app.src.dependencies import (get_current_user_by_access_token, get_data_by_refresh_token,
                                      verify_csrf_token)
from web_app.src.schemas import (CreateEventRequest, UpdateEventRequest, AddParticipantRequest,
                                 UpdateParticipantRequest, AddAccessUserEventRequest)
from web_app.src.utils import redis_service, ensure_user_access, ensure_user_event_access


router = APIRouter(
    prefix="/api/v1/event",
    tags=["API"]
)


@router.post(
    path="/create",
    response_class=JSONResponse,
    summary="Создать мероприятие"
)
async def create_event(
    data: CreateEventRequest,
    current_user: User = Depends(get_current_user_by_access_token),
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token),
    csrf_user_id: str = Depends(verify_csrf_token)
):
    ensure_user_access(
        user=current_user,
        token_data=token_data,
        user_id=csrf_user_id
    )

    return await redis_service.add_event(
        user_id=current_user.id,
        data=data
    )


@router.patch(
    path="/{event_id}",
    response_class=JSONResponse,
    summary="Обновить мероприятие"
)
async def update_event(
    event_id: UUID,
    data: UpdateEventRequest,
    current_user: User = Depends(get_current_user_by_access_token),
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token),
    csrf_user_id: str = Depends(verify_csrf_token)
):
    ensure_user_access(
        user=current_user,
        token_data=token_data,
        user_id=csrf_user_id
    )

    await ensure_user_event_access(
        event_id=event_id,
        user_id=current_user.id
    )

    return await redis_service.update_event(
        event_id=str(event_id),
        title=data.title,
        start_datetime=data.start_datetime,
        end_datetime=data.end_datetime,
        access_users=data.access_users
    )


@router.delete(
    path="/{event_id}",
    response_class=JSONResponse,
    summary="Удалить мероприятие"
)
async def delete_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user_by_access_token),
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token),
    csrf_user_id: str = Depends(verify_csrf_token)
):
    ensure_user_access(
        user=current_user,
        token_data=token_data,
        user_id=csrf_user_id
    )

    await ensure_user_event_access(
        event_id=event_id,
        user_id=current_user.id
    )

    return await redis_service.delete_event(
        event_id=str(event_id),
        user_id=current_user.id
    )


@router.post(
    path="/{event_id}/participant",
    response_class=JSONResponse,
    summary="Добавить участника"
)
async def add_participant(
    event_id: UUID,
    data: AddParticipantRequest,
    current_user: User = Depends(get_current_user_by_access_token),
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token),
    csrf_user_id: str = Depends(verify_csrf_token)
):
    ensure_user_access(
        user=current_user,
        token_data=token_data,
        user_id=csrf_user_id
    )

    await ensure_user_event_access(
        event_id=event_id,
        user_id=current_user.id
    )

    return await redis_service.add_participant(
        event_id=str(event_id),
        full_name=data.full_name,
        extra_info=data.extra_info
    )


@router.patch(
    path="/{event_id}/participant/{participant_id}",
    response_class=JSONResponse,
    summary="Обновить участника"
)
async def update_participant(
    event_id: UUID,
    participant_id: UUID,
    data: UpdateParticipantRequest,
    current_user: User = Depends(get_current_user_by_access_token),
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token),
    csrf_user_id: str = Depends(verify_csrf_token)
):
    ensure_user_access(
        user=current_user,
        token_data=token_data,
        user_id=csrf_user_id
    )

    await ensure_user_event_access(
        event_id=event_id,
        user_id=current_user.id
    )

    return await redis_service.update_participant(
        participant_id=str(participant_id),
        full_name=data.full_name,
        extra_info=data.extra_info
    )


@router.delete(
    path="/{event_id}/participant/{participant_id}",
    response_class=JSONResponse,
    summary="Удалить участника"
)
async def delete_participant(
    event_id: UUID,
    participant_id: UUID,
    current_user: User = Depends(get_current_user_by_access_token),
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token),
    csrf_user_id: str = Depends(verify_csrf_token)
):
    ensure_user_access(
        user=current_user,
        token_data=token_data,
        user_id=csrf_user_id
    )

    await ensure_user_event_access(
        event_id=event_id,
        user_id=current_user.id
    )

    return await redis_service.remove_participant(
        event_id=str(event_id),
        participant_id=str(participant_id)
    )


@router.post(
    path="/{event_id}/access",
    response_class=JSONResponse,
    summary="Добавить доступ пользователю к мероприятию"
)
async def add_access_user(
    event_id: UUID,
    data: AddAccessUserEventRequest,
    current_user: User = Depends(get_current_user_by_access_token),
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token),
    csrf_user_id: str = Depends(verify_csrf_token)
):
    ensure_user_access(
        user=current_user,
        token_data=token_data,
        user_id=csrf_user_id
    )

    await ensure_user_event_access(
        event_id=event_id,
        user_id=current_user.id,
        only_owner=True
    )

    return await redis_service.add_access_user(
        event_id=str(event_id),
        target_user_id=data.target_user_id
    )


@router.delete(
    path="/{event_id}/access/{target_user_id}",
    response_class=JSONResponse,
    summary="Удалить доступ пользователю к мероприятию"
)
async def delete_access_user(
    event_id: UUID,
    target_user_id: int,
    current_user: User = Depends(get_current_user_by_access_token),
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token),
    csrf_user_id: str = Depends(verify_csrf_token)
):
    ensure_user_access(
        user=current_user,
        token_data=token_data,
        user_id=csrf_user_id
    )

    await ensure_user_event_access(
        event_id=event_id,
        user_id=current_user.id,
        only_owner=True
    )

    return await redis_service.remove_access_user(
        event_id=str(event_id),
        target_user_id=target_user_id
    )