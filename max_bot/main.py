# Внешние зависимости
import asyncio
import logging
# Внутренние модули
from max_bot.core import dp, bot
from max_bot.middlewares import LoggingMiddleware
from max_bot.handlers import main_router
from max_bot.utils import redis_service


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    logging.info("Инициализируем redis")
    await redis_service.init_redis()

    dp.outer_middleware(LoggingMiddleware())
    dp.include_routers(main_router)

    await dp.start_polling(bot)


def main_run():
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())