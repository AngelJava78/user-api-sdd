"""Entidad User (spec/domain/user.md)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

from app.domain.value_objects import Email, PersonName


@dataclass(kw_only=True)
class User:
    id: UUID
    email: Email
    name: PersonName
    lastname: PersonName
    second_lastname: PersonName | None
    status: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        email: Email,
        name: PersonName,
        lastname: PersonName,
        second_lastname: PersonName | None,
        now: datetime,
    ) -> Self:
        """Un usuario nuevo es activo y su id lo genera el sistema (FR-003)."""
        return cls(
            id=uuid4(),
            email=email,
            name=name,
            lastname=lastname,
            second_lastname=second_lastname,
            status=True,
            created_at=now,
            updated_at=now,
        )
