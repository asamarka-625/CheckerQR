# Внутренние модули
from shared_services import RedisService
from max_bot.utils.phone import normalize_phone
from max_bot.utils.qr import generate_qr_bytes
from max_bot.core import cfg


redis_service = RedisService(
    redis_url=cfg.redis_url
)

