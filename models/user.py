# Внешние зависимости
import sqlalchemy.orm as so
import sqlalchemy as sa
# Внутренние модули
from models.base import Base


# Пользователи
class User(Base):
    __tablename__ = "users"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    full_name: so.Mapped[str] = so.mapped_column(
        sa.String(128),
        index=True,
        nullable=False
    )
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64),
        nullable=False,
        unique=True
    )
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.username})>"

    def __str__(self):
        return f"[{self.id}] {self.full_name}"
