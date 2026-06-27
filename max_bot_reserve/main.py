# Внешние зависимости
import asyncio
import logging
# Внутренние модули
from max_bot_reserve.core import dp, bot
from max_bot_reserve.middlewares import LoggingMiddleware
from max_bot_reserve.handlers import main_router


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    dp.outer_middleware(LoggingMiddleware())
    dp.include_routers(main_router)

    await dp.start_polling(bot)


def main_run():
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())