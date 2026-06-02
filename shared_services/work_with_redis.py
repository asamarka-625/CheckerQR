# Внешние зависимости
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import redis.asyncio as redis
from fastapi import HTTPException, status


# Класс по работе Redis
class RedisService:
    def __init__(
        self,
        redis_url: str,
        refresh_token_expire_minutes: int = 21600
    ):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None

        self.REFRESH_TOKEN_EXPIRE_MINUTES = refresh_token_expire_minutes

        self.refresh_prefix = "refresh:"
        self.user_set_prefix = "user_tokens:"

        self.event_prefix = "event:"
        self.participant_prefix = "participant_prefix:"

        self.user = "user:"

    async def init_redis(self):
        """Инициализация подключения к Redis"""
        if not self.redis:
            self.redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )

    async def close_redis(self):
        """Закрытие подключения к Redis"""
        if self.redis:
            await self.redis.close()

    async def add_user_refresh_token(
        self,
        user_id: str,
        refresh_uuid: str,
        data: str
    ):
        """Добавление токена и индексация его в сете пользователя"""
        token_key = f"{self.refresh_prefix}{user_id}:{refresh_uuid}"
        set_key = f"{self.user_set_prefix}{user_id}"

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.set(
                name=token_key,
                value=data,
                ex=self.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            )
            pipe.sadd(set_key, refresh_uuid)
            # Устанавливаем TTL для всего сета (чуть больше токена, для очистки)
            pipe.expire(set_key, self.REFRESH_TOKEN_EXPIRE_MINUTES * 60 + 3600)
            await pipe.execute()

    async def update_user_refresh_token(
        self,
        user_id: str,
        refresh_uuid: str,
        data: str,
        last_token: str
    ):
        """Обновление токена и индексация его в сете пользователя"""
        old_token_key = f"{self.refresh_prefix}{user_id}:{last_token}"
        new_token_key = f"{self.refresh_prefix}{user_id}:{refresh_uuid}"
        set_key = f"{self.user_set_prefix}{user_id}"

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.expire(old_token_key, 30)
            pipe.set(
                name=new_token_key,
                value=data,
                ex=self.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            )
            pipe.sadd(set_key, refresh_uuid)
            # Устанавливаем TTL для всего сета (чуть больше токена, для очистки)
            pipe.expire(set_key, self.REFRESH_TOKEN_EXPIRE_MINUTES * 60 + 3600)
            await pipe.execute()

    async def del_user_refresh_token(self, user_id: str, refresh_uuid: str):
        """Удаление конкретного токена"""
        token_key = f"{self.refresh_prefix}{user_id}:{refresh_uuid}"
        set_key = f"{self.user_set_prefix}{user_id}"

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.delete(token_key)
            pipe.srem(set_key, refresh_uuid)
            await pipe.execute()

    async def del_other_user_refresh_tokens(self, user_id: str, current_refresh_uuid: str):
        """Удаляем все сессии пользователя, кроме текущей"""
        set_key = f"{self.user_set_prefix}{user_id}"

        # Получаем все UUID сессий пользователя
        all_uuids = await self.redis.smembers(set_key)

        async with self.redis.pipeline(transaction=True) as pipe:
            for r_uuid in all_uuids:
                if r_uuid != current_refresh_uuid:
                    # Удаляем данные токена
                    pipe.delete(f"{self.refresh_prefix}{user_id}:{r_uuid}")
                    # Удаляем UUID из сета
                    pipe.srem(set_key, r_uuid)
            await pipe.execute()

    async def is_refresh_token_valid(self, user_id: str, refresh_uuid: str) -> bool:
        """Проверка валидности (есть ли UUID в сете и существует ли сам токен)"""
        token_key = f"{self.refresh_prefix}{user_id}:{refresh_uuid}"
        exists = await self.redis.exists(token_key)

        if not exists:
            await self.redis.srem(f"{self.user_set_prefix}{user_id}", refresh_uuid)
            return False
        return True

    async def add_event(
        self,
        user_id: int,
        data: Any
    ) -> Dict[str, str]:
        """Атомарное создание события (Redis HASH + SET архитектура)"""
        title = data.title.strip()
        event_id = str(uuid.uuid4())

        event_key = f"{self.event_prefix}{event_id}"
        participants_set_key = f"{event_key}:participants"

        # 1. TTL
        ttl_seconds = int(
            (data.end_datetime - datetime.now(timezone.utc)).total_seconds()
        )

        if ttl_seconds <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Время окончания уже в прошлом"
            )

        async with self.redis.pipeline(transaction=True) as pipe:
            # 2. подготовка участников
            participant_keys = []

            for p in data.participants:
                participant_id = str(uuid.uuid4())
                participant_key = f"{self.participant_prefix}{participant_id}"

                participant_keys.append(participant_id)

                # HASH участника
                pipe.hset(
                    participant_key,
                    mapping={
                        "event_id": event_id,
                        "event_title": title,
                        "full_name": p.full_name,
                        "extra_info": p.extra_info
                    }
                )

                # TTL участника
                pipe.expire(participant_key, ttl_seconds)

                # связь event → participant
                pipe.sadd(participants_set_key, participant_id)

            # 3. HASH события
            pipe.hset(
                event_key,
                mapping={
                    "title": title,
                    "user_id": user_id,
                    "start_datetime": data.start_datetime.isoformat(),
                    "end_datetime": data.end_datetime.isoformat(),
                }
            )

            access_users_key = f"{event_key}:access_users"
            for uid in data.access_users:
                pipe.sadd(access_users_key, uid)

            pipe.expire(access_users_key, ttl_seconds)

            # TTL event + set
            pipe.expire(event_key, ttl_seconds)
            pipe.expire(participants_set_key, ttl_seconds)

            pipe.sadd(f"{self.user}{user_id}:events", event_id)

            # 4. EXEC (атомарно)
            await pipe.execute()

        return {
            "event_id": event_id,
            "status": "created"
        }

    async def get_event_with_participants(
        self,
        event_id: str
    ) -> Dict[str, Any]:
        """Получить событие со всеми участниками"""

        event_key = f"{self.event_prefix}{event_id}"
        participants_set_key = f"{event_key}:participants"

        async with self.redis.pipeline(transaction=True) as pipe:
            # 1. событие
            pipe.hgetall(event_key)

            # 2. список участников UUID
            pipe.smembers(participants_set_key)

            result = await pipe.execute()

        event_data, participant_ids = result
        # если события нет
        if not event_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        participants = []

        # 3. добираем участников
        async with self.redis.pipeline(transaction=True) as pipe:
            for pid in participant_ids:
                participant_key = f"{self.participant_prefix}{pid}"
                pipe.hgetall(participant_key)

            participants_raw = await pipe.execute()

        for pid, pdata in zip(participant_ids, participants_raw):
            if pdata:  # защита от протухших ключей
                participants.append({
                    "participant_id": pid,
                    "full_name": pdata.get("full_name"),
                    "extra_info": pdata.get("extra_info")
                })

        access_users = await self.redis.smembers(f"{event_key}:access_users")

        # Redis возвращает bytes/str → нормализуем
        access_users = [int(uid) for uid in access_users]

        return {
            "event_id": event_id,
            "title": event_data.get("title"),
            "start_datetime": datetime.fromisoformat(event_data["start_datetime"]) \
                if event_data.get("start_datetime") else None,
            "end_datetime": datetime.fromisoformat(event_data["end_datetime"]) \
                if event_data.get("start_datetime") else None,
            "participants": participants,
            "access_users": list(set(access_users))
        }

    async def get_participant(
        self,
        participant_id: str
    ) -> Dict[str, str]:
        """Получить участника по uuid"""
        participant_key = f"{self.participant_prefix}{participant_id}"

        data = await self.redis.hgetall(participant_key)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Участник не найден"
            )

        return {
            "participant_id": participant_id,
            "event_id": data.get("event_id"),
            "event_title": data.get("event_title"),
            "full_name": data.get("full_name"),
            "extra_info": data.get("extra_info"),
        }

    async def add_participant(
        self,
        event_id: str,
        full_name: str,
        extra_info: str
    ):
        """Добавление участника в событие"""
        event_key = f"{self.event_prefix}{event_id}"
        participants_set_key = f"{event_key}:participants"

        # 1. проверяем событие
        event_data = await self.redis.hgetall(event_key)
        if not event_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        # 2. TTL берем из события
        end_datetime = datetime.fromisoformat(event_data["end_datetime"])

        ttl_seconds = int(
            (end_datetime - datetime.now(timezone.utc)).total_seconds()
        )

        if ttl_seconds <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Событие уже завершено"
            )

        participant_id = str(uuid.uuid4())
        participant_key = f"{self.participant_prefix}{participant_id}"

        async with self.redis.pipeline(transaction=True) as pipe:
            # participant HASH
            pipe.hset(
                participant_key,
                mapping={
                    "event_id": event_id,
                    "event_title": event_data["title"],
                    "full_name": full_name,
                    "extra_info": extra_info
                }
            )

            # связь event → participant
            pipe.sadd(participants_set_key, participant_id)

            # TTL
            pipe.expire(participant_key, ttl_seconds)
            pipe.expire(participants_set_key, ttl_seconds)

            await pipe.execute()

        return {
            "participant_id": participant_id,
            "status": "added"
        }

    async def remove_participant(
        self,
        event_id: str,
        participant_id: str
    ):
        """Удаление участника из события"""
        event_key = f"{self.event_prefix}{event_id}"
        participants_set_key = f"{event_key}:participants"
        participant_key = f"{self.participant_prefix}{participant_id}"

        # 1. проверка существования события
        if not await self.redis.exists(event_key):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        async with self.redis.pipeline(transaction=True) as pipe:
            # удалить связь
            pipe.srem(participants_set_key, participant_id)

            # удалить сам participant
            pipe.delete(participant_key)

            await pipe.execute()

        return {
            "participant_id": participant_id,
            "status": "deleted"
        }

    async def update_participant(
        self,
        participant_id: str,
        full_name: str | None = None,
        extra_info: str | None = None
    ) -> Dict[str, str]:
        """Обновление данных участника"""
        participant_key = f"{self.participant_prefix}{participant_id}"

        # 1. загрузка текущих данных
        participant_data = await self.redis.hgetall(participant_key)

        if not participant_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Участник не найден"
            )

        # 2. обновление полей
        updated_data = {}
        if full_name is not None:
            updated_data["full_name"] = full_name

        if extra_info is not None:
            updated_data["extra_info"] = extra_info

        if not updated_data:
            return {
                "participant_id": participant_id,
                "status": "nothing_to_update"
            }

        # 5. обновление HASH
        await self.redis.hset(
            participant_key,
            mapping=updated_data
        )

        return {
            "participant_id": participant_id,
            "status": "updated"
        }

    async def get_user_events(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        index_key = f"{self.user}{user_id}:events"

        event_ids = await self.redis.smembers(index_key)
        if not event_ids:
            return []

        events = []
        deleted_event_ids = []

        async with self.redis.pipeline(transaction=True) as pipe:
            for event_id in event_ids:
                event_key = f"{self.event_prefix}{event_id}"
                pipe.hgetall(event_key)

            results = await pipe.execute()

        # 1. обработка результатов
        for event_id, data in zip(event_ids, results):
            if not data:
                # ❌ event умер → нужно удалить из index
                deleted_event_ids.append(event_id)
                continue

            events.append({
                "event_id": event_id,
                "title": data.get("title"),
                "start_datetime": datetime.fromisoformat(data["start_datetime"]) \
                    if data.get("start_datetime") else None,
                "end_datetime": datetime.fromisoformat(data["end_datetime"]) \
                    if data.get("end_datetime") else None
            })

        # 2. чистим мусор из SET
        if deleted_event_ids:
            async with self.redis.pipeline(transaction=True) as pipe:
                for event_id in deleted_event_ids:
                    pipe.srem(index_key, event_id)
                await pipe.execute()

        return events

    async def delete_event(
        self,
        event_id: str,
        user_id: int
    ) -> Dict[str, str]:
        """Удаление мероприятия полностью"""

        event_key = f"{self.event_prefix}{event_id}"
        participants_key = f"{event_key}:participants"
        index_key = f"{self.user}{user_id}:events"

        # 1. проверяем событие
        event_data = await self.redis.hgetall(event_key)
        if not event_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        if int(event_data.get("user_id", 0)) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав"
            )

        # 2. получаем участников
        participant_ids = await self.redis.smembers(participants_key)

        async with self.redis.pipeline(transaction=True) as pipe:
            # 3. удалить участников
            for pid in participant_ids:
                pipe.delete(f"{self.participant_prefix}{pid}")

            # 4. удалить event и set
            pipe.delete(event_key)
            pipe.delete(participants_key)

            # 5. удалить из индекса
            pipe.srem(index_key, event_id)

            await pipe.execute()

        return {
            "status": "deleted",
            "event_id": event_id
        }

    async def update_event(
        self,
        event_id: str,
        title: str | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        access_users: List[int] | None = None
    ) -> Dict[str, str]:
        """Обновление мероприятия"""

        event_key = f"{self.event_prefix}{event_id}"
        participants_key = f"{event_key}:participants"

        event_data = await self.redis.hgetall(event_key)
        if not event_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        update_data = {}

        # 1. обновление полей
        if title is not None:
            update_data["title"] = title.strip()

        if start_datetime is not None:
            update_data["start_datetime"] = start_datetime.isoformat()

        if end_datetime is not None:
            update_data["end_datetime"] = end_datetime.isoformat()

        if update_data:
            await self.redis.hset(event_key, mapping=update_data)

        # 2. пересчёт TTL (если изменили end_datetime)
        final_end = end_datetime or datetime.fromisoformat(event_data["end_datetime"])

        ttl_seconds = int(
            (final_end - datetime.now(timezone.utc)).total_seconds()
        )

        if ttl_seconds <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Время окончания уже в прошлом"
            )

        # 3. обновляем TTL всех ключей
        participant_ids = await self.redis.smembers(participants_key)

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.expire(event_key, ttl_seconds)
            pipe.expire(participants_key, ttl_seconds)

            if access_users is not None:
                access_users_key = f"{event_key}:access_users"
                pipe.delete(access_users_key)  # удалить старые

                if access_users:
                    pipe.sadd(access_users_key, *access_users)  # добавить новые

                pipe.expire(access_users_key, ttl_seconds)

            for pid in participant_ids:
                if update_data.get("title") is not None:
                    pipe.hset(
                        f"{self.participant_prefix}{pid}",
                        mapping={
                            "event_title": update_data["title"]
                        }
                    )

                pipe.expire(f"{self.participant_prefix}{pid}", ttl_seconds)

            await pipe.execute()

        return {
            "status": "updated",
            "event_id": event_id
        }

    async def check_event_access(
        self,
        event_id: str,
        user_id: int,
        only_owner: bool = False
    ):
        """Проверка доступа до события"""
        event_key = f"{self.event_prefix}{event_id}"
        access_key = f"{event_key}:access_users"

        # владелец всегда имеет доступ
        event = await self.redis.hgetall(event_key)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        if only_owner and int(event.get("user_id", 0)) != user_id:
            return False

        if int(event.get("user_id", 0)) == user_id:
            return True

        # проверка ACL
        return await self.redis.sismember(access_key, user_id)

    async def get_event_access_users(
        self,
        event_id: str
    ) -> List[str]:
        """Список пользователей с доступом к событию"""
        key = f"{self.event_prefix}{event_id}:access_users"
        return list(await self.redis.smembers(key))

    async def add_access_user(
        self,
        event_id: str,
        target_user_id: int
    ) -> Dict[str, str | int]:
        """Добавить пользователя в доступ к событию"""

        event_key = f"{self.event_prefix}{event_id}"
        access_key = f"{event_key}:access_users"

        # 1. проверка события
        event = await self.redis.hgetall(event_key)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        # 2. добавляем доступ
        await self.redis.sadd(access_key, target_user_id)

        return {
            "event_id": event_id,
            "user_id": target_user_id,
            "status": "access_granted"
        }

    async def remove_access_user(
        self,
        event_id: str,
        target_user_id: int
    ) -> Dict[str, str | int]:
        """Убрать пользователя из доступа к событию"""

        event_key = f"{self.event_prefix}{event_id}"
        access_key = f"{event_key}:access_users"

        # 1. проверка события
        event = await self.redis.hgetall(event_key)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Событие не найдено"
            )

        # 2. удаляем доступ
        await self.redis.srem(access_key, target_user_id)

        return {
            "event_id": event_id,
            "user_id": target_user_id,
            "status": "access_revoked"
        }