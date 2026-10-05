"""Caso de uso: listar usuarios activos paginados (US-2; FR-001)."""

from app.application.dto import UserPage
from app.domain.repository import UserRepository


async def list_users(*, limit: int, offset: int, repository: UserRepository) -> UserPage:
    """`limit` y `offset` llegan ya validados por la capa API (contrato y Settings)."""
    items = await repository.list_active(limit, offset)
    total = await repository.count_active()
    return UserPage(items=items, total=total, limit=limit, offset=offset)
