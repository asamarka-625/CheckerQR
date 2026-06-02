# Внутренние модули
from shared_services import RedisService
from max_bot.core import cfg


redis_service = RedisService(
    redis_url=cfg.redis_url
)

