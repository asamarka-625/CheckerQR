# Внешние зависимости
import logging
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Dict, Awaitable
from maxapi.filters.middleware import BaseMiddleware
from maxapi.types import MessageCreated, MessageCallback


class LoggingMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        file_handler = RotatingFileHandler(
            filename='logs/max_bot_reserve.log',
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,  # храним 5 backup файлов
            encoding='utf-8'
        )

        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        logger.addHandler(file_handler)

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user

        if isinstance(event, MessageCreated):
            message_body = event.message.body
            if message_body and hasattr(message_body, 'text'):
                text = message_body.text

            else:
                text = 'отправлен объект'

            logging.info(f'Received MESSAGE from [{user.user_id}]: [{text}]')

        # Обработка callback-запросов
        elif isinstance(event, MessageCallback):
            callback_data = event.callback.payload
            logging.info(f'Received CALLBACK from [{user.user_id}]: [{callback_data}]')

        # Обработка других типов событий
        else:
            event_type = type(event).__name__
            logging.info(f'Received {event_type}')

        return await handler(event, data)