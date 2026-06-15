# Внешние зависимости
from typing import Dict
from uuid import UUID
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
# Внутренние модули
from web_app.src.dependencies import get_data_by_refresh_token
from web_app.src.utils import redis_service, ensure_user_event_access
from web_app.src.crud import sql_get_users_by_ids
from web_app.src.core import cfg


router = APIRouter()
templates = Jinja2Templates(directory="web_app/templates")


# Страница аутентификации
@router.get(
    "/login",
    response_class=HTMLResponse,
    summary="Страница аутентификации"
)
async def login_page(
    request: Request
):
    context = {
        "prefix": cfg.URL_PREFIX
    }

    return templates.TemplateResponse(
        name="login.html",
        request=request,
        context=context
    )


# Страница создания мероприятия
@router.get(
    "/create-event",
    response_class=HTMLResponse,
    summary="Страница создания мероприятия"
)
async def create_event_page(
    request: Request,
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token)
):
    context = {
        "prefix": cfg.URL_PREFIX
    }

    return templates.TemplateResponse(
        name="create_event.html",
        request=request,
        context=context
    )


# Страница с мероприятиями пользователя
@router.get(
    "/events",
    response_class=HTMLResponse,
    summary="Страница с мероприятиями пользователя"
)
async def events_page(
    request: Request,
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token)
):
    events = await redis_service.get_user_events(
        user_id=int(token_data["user_id"])
    )

    context = {
        "prefix": cfg.URL_PREFIX,
        "events": events
    }

    return templates.TemplateResponse(
        name="events.html",
        request=request,
        context=context
    )


# Страница с деталями мероприятия
@router.get(
    "/event/{event_id}",
    response_class=HTMLResponse,
    summary="Страница с деталями мероприятия"
)
async def event_detail_page(
    request: Request,
    event_id: UUID,
    page: int = Query(1, ge=1),
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token)
):
    await ensure_user_event_access(
        event_id=event_id,
        user_id=int(token_data["user_id"])
    )

    event_detail = await redis_service.get_event_with_participants_paginated(
        event_id=str(event_id),
        page=page,
        page_size=20
    )

    context = {
        "prefix": cfg.URL_PREFIX,
        "username_max_bot": cfg.USERNAME_MAX_BOT,
        **event_detail
    }

    return templates.TemplateResponse(
        name="event_detail.html",
        request=request,
        context=context
    )


# Страница обновления мероприятия
@router.get(
    "/event/edit/{event_id}",
    response_class=HTMLResponse,
    summary="Страница с мероприятиями пользователя"
)
async def update_event_page(
    request: Request,
    event_id: UUID,
    token_data: Dict[str, str] = Depends(get_data_by_refresh_token)
):
    await ensure_user_event_access(
        event_id=event_id,
        user_id=int(token_data["user_id"])
    )

    event_detail = await redis_service.get_event_with_participants(
        event_id=str(event_id)
    )

    del event_detail["participants"]

    access_users = await sql_get_users_by_ids(
        ids=event_detail["access_users"]
    )

    context = {
        "prefix": cfg.URL_PREFIX,
        **event_detail,
        "access_users": [u.model_dump() for u in access_users]
    }

    return templates.TemplateResponse(
        name="event_edit.html",
        request=request,
        context=context
    )