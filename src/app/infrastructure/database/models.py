"""Modelos ORM de SQLAlchemy."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, MetaData, String, text, true
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Nombres deterministas para restricciones e índices: hacen reproducibles
# las migraciones y sus downgrade (NFR-006).
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class UserModel(Base):
    """Tabla `users` (spec/data/schema.md; migración 5a2a164feec3)."""

    __tablename__ = "users"
    __table_args__ = (
        Index("ux_users_email_lower", text("lower(email)"), unique=True),
        Index("ix_users_status_created_at", "status", "created_at", "id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320))
    name: Mapped[str] = mapped_column(String(30))
    lastname: Mapped[str] = mapped_column(String(30))
    second_lastname: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[bool] = mapped_column(server_default=true())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
