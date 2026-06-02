# Внешние зависимости
from typing import Optional, Dict
from datetime import datetime, timedelta, UTC
import uuid
import jwt
from fastapi import HTTPException, status, Depends, Cookie, Header
from fastapi.security import OAuth2PasswordBearer
# Внутренние модули
from models import User
from web_app.src.utils import verify_password, redis_service
from web_app.src.crud import sql_get_user_by_username, sql_get_user_by_id
from web_app.src.core import cfg



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


# Аутентификация пользователя
async def authenticate_user(username: str, password: str) -> Optional[User]:
    user = await sql_get_user_by_username(
        username=username,
        not_found_error=False
    )
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


# Создание JWT токена
def create_jwt_token(
    data: dict,
    expires_minutes: int,
    secret_key: str
) -> str:
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(UTC)
    })
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=cfg.ALGORITHM)

    return encoded_jwt


# Создание refresh токена
async def create_refresh_token(
    user_id: str,
    user_agent: str,
    ip: str,
    last_token: Optional[str] = None
) -> str:
    jti = str(uuid.uuid4())
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M")

    refresh_token = create_jwt_token(
        data={
            "sub": user_id,
            "type": "refresh",
            "jti": jti
        },
        expires_minutes=cfg.REFRESH_TOKEN_EXPIRE_MINUTES,
        secret_key=cfg.SECRET_REFRESH_KEY
    )

    if last_token is None:
        await redis_service.add_user_refresh_token(
            user_id=user_id,
            refresh_uuid=jti,
            data=f"Сессия открыта {now}, {user_agent}, {ip}"
        )

    else:
        await redis_service.update_user_refresh_token(
            user_id=user_id,
            refresh_uuid=jti,
            data=f"Сессия открыта {now}, {user_agent}, {ip}",
            last_token=last_token
        )

    return refresh_token


# Создание access токена
def create_access_token(user_id: str) -> str:
    access_token = create_jwt_token(
        data={
            "sub": user_id,
            "type": "access"
        },
        expires_minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES,
        secret_key=cfg.SECRET_ACCESS_KEY
    )

    return access_token


# Создание csrf токена
def create_csrf_token(user_id: str) -> str:
    csrf_token = create_jwt_token(
        data={
            "sub": user_id,
            "type": "csrf"
        },
        expires_minutes=cfg.CSRF_TOKEN_EXPIRE_MINUTES,
        secret_key=cfg.SECRET_CSRF_KEY
    )

    return csrf_token


# Получаем пользователя по access токену
async def get_current_user_by_access_token(
    access_token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    if not access_token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            access_token,
            cfg.SECRET_ACCESS_KEY,
            algorithms=[cfg.ALGORITHM],
            leeway=10
        )
        user_id: str = payload.get("sub")
        type_token: str = payload.get("type")

        if user_id is None or type_token != "access":
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception

    user = await sql_get_user_by_id(user_id=int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# Получаем данные refresh токена
async def get_data_by_refresh_token(
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token")
) -> Dict[str, str]:
    if not refresh_token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            refresh_token,
            cfg.SECRET_REFRESH_KEY,
            algorithms=[cfg.ALGORITHM],
            leeway=10
        )
        user_id: str = payload.get("sub")
        type_token: str = payload.get("type")
        jti: str = payload.get("jti")

        if user_id is None or jti is None or type_token != "refresh":
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception

    if not await redis_service.is_refresh_token_valid(user_id=user_id, refresh_uuid=jti):
        raise credentials_exception

    return {
        "user_id": user_id,
        "jti": jti
    }


# Проверяет наличие и валидность CSRF токена из заголовков
async def verify_csrf_token(
    x_csrf_token: str = Header(None, alias="X-CSRF-Token")
) -> str:
    if not x_csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing"
        )

    try:
        payload = jwt.decode(
            x_csrf_token,
            cfg.SECRET_CSRF_KEY,
            algorithms=[cfg.ALGORITHM]
        )

        user_id: str = payload.get("sub")
        type_token: str = payload.get("type")

        if user_id is None or type_token != "csrf":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token type"
            )

        return user_id

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired CSRF token"
        )