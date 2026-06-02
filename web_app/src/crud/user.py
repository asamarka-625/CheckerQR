# Внешние зависимости
from typing import Optional, List
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from fastapi import HTTPException, status
# Внутренние модули
from models import User
from web_app.src.core import cfg, connection
from web_app.src.schemas import UserScheme


# Получаем пользователя по username
@connection
async def sql_get_user_by_username(
    username: str,
    session: AsyncSession,
    not_found_error: bool = True
) -> Optional[User]:
    try:
        user_result = await session.execute(
            sa.select(User)
            .where(User.username == username)
        )

        if not_found_error:
            user = user_result.scalar_one()

        else:
            user = user_result.scalar_one_or_none()

        return user

    except NoResultFound:
        cfg.logger.info(f"User not found by username: {username}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    except SQLAlchemyError as e:
        cfg.logger.error(f"Database error get user by username: {username}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    except Exception as e:
        cfg.logger.error(f"Unexpected error get user by username: {username}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected server error")


# Получаем пользователя по id
@connection
async def sql_get_user_by_id(
    user_id: int,
    session: AsyncSession
) -> User:
    try:
        user_result = await session.execute(
            sa.select(User)
            .where(User.id == user_id)
        )
        user = user_result.scalar_one()

        return user

    except NoResultFound:
        cfg.logger.info(f"User not found by id: {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    except SQLAlchemyError as e:
        cfg.logger.error(f"Database error get user by id: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    except Exception as e:
        cfg.logger.error(f"Unexpected error get user by id: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected server error")


# Получаем пользователей по имени
@connection
async def sql_get_users_by_name(
    name: str,
    session: AsyncSession,
) -> List[UserScheme]:
    try:
        users_result = await session.execute(
            sa.select(User)
            .where(User.full_name.ilike(f"%{name}%"))
        )
        users = users_result.scalars()


        return [
            UserScheme.model_validate(user)
            for user in users
        ]

    except SQLAlchemyError as e:
        cfg.logger.error(f"Database error get users by name: {name}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    except Exception as e:
        cfg.logger.error(f"Unexpected error get users by name: {name}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected server error")


# Получаем пользователей по IDS
@connection
async def sql_get_users_by_ids(
    ids: List[int],
    session: AsyncSession,
) -> List[UserScheme]:
    try:
        users_result = await session.execute(
            sa.select(User)
            .where(User.id.in_(ids))
        )
        users = users_result.scalars()


        return [
            UserScheme.model_validate(user)
            for user in users
        ]

    except SQLAlchemyError as e:
        cfg.logger.error(f"Database error get users by ids: {ids}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    except Exception as e:
        cfg.logger.error(f"Unexpected error get users by ids: {ids}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected server error")