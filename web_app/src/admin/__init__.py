from web_app.src.admin.user import UserAdmin
from web_app.src.admin.authentication import BasicAuthBackend
# Внутренние модули
from web_app.src.core import cfg


authentication_backend = BasicAuthBackend(secret_key=cfg.SECRET_REFRESH_KEY)