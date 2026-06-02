# Внешние зависимости
from maxapi import Bot, Dispatcher
from maxapi.enums.parse_mode import ParseMode
from maxapi.client.default import DefaultConnectionProperties
# Внутренние модули
from max_bot.core.config import cfg


bot = Bot(
    token=cfg.MAX_BOT_TOKEN,
    parse_mode=ParseMode.HTML,
    default_connection=DefaultConnectionProperties(
        proxy=cfg.PROXY
    )
)

dp = Dispatcher()