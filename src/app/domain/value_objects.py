"""Value objects del dominio (FR-005, FR-006; spec/domain/user.md)."""

from dataclasses import dataclass
from typing import Self

from app.domain.errors import InvalidUserData

EMAIL_MAX_LENGTH = 320
EMAIL_LOCAL_MAX_LENGTH = 64
EMAIL_TLD_MIN_LENGTH = 2
NAME_MAX_LENGTH = 30
NAME_ALLOWED_SYMBOLS = frozenset(" -'")


def _invalid(field: str, message: str) -> InvalidUserData:
    return InvalidUserData(f"Invalid {field}", details={field: message})


@dataclass(frozen=True, slots=True)
class Email:
    """Email normalizado (sin espacios en los extremos y en minúsculas) e inmutable."""

    value: str

    @classmethod
    def parse(cls, raw: str) -> Self:
        value = raw.strip().lower()
        if not _is_valid_email(value):
            raise _invalid("email", "Invalid email format")
        return cls(value)


def _is_valid_email(value: str) -> bool:
    if len(value) > EMAIL_MAX_LENGTH or value.count("@") != 1:
        return False
    if any(char.isspace() for char in value):
        return False
    local, domain = value.split("@")
    if not 1 <= len(local) <= EMAIL_LOCAL_MAX_LENGTH:
        return False
    labels = domain.split(".")
    return len(labels) >= 2 and all(labels) and len(labels[-1]) >= EMAIL_TLD_MIN_LENGTH


@dataclass(frozen=True, slots=True)
class PersonName:
    """Nombre o apellido: de 1 a 30 letras, espacios, guiones o apóstrofos; empieza con letra."""

    value: str

    @classmethod
    def parse(cls, raw: str, *, field: str) -> Self:
        value = raw.strip()
        if not 1 <= len(value) <= NAME_MAX_LENGTH:
            raise _invalid(field, f"Must be between 1 and {NAME_MAX_LENGTH} characters")
        if not value[0].isalpha():
            raise _invalid(field, "Must start with a letter")
        if not all(char.isalpha() or char in NAME_ALLOWED_SYMBOLS for char in value):
            raise _invalid(field, "Only letters, spaces, hyphens and apostrophes are allowed")
        return cls(value)

    @classmethod
    def parse_optional(cls, raw: str | None, *, field: str) -> Self | None:
        """Un valor ausente o en blanco se trata como `null`."""
        if raw is None or not raw.strip():
            return None
        return cls.parse(raw, field=field)
