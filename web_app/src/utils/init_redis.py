from shared_services import RedisService
from web_app.src.core import cfg


redis_service = RedisService(
    redis_url=cfg.redis_url,
    refresh_token_expire_minutes=cfg.REFRESH_TOKEN_EXPIRE_MINUTES
)