"""Value object Email: normalización y formato (FR-005, spec/domain/user.md)."""

import pytest

from app.domain.errors import InvalidUserData
from app.domain.value_objects import Email

MAX_LOCAL = "a" * 64
MAX_DOMAIN = "b" * 251 + ".com"  # 255 caracteres


def test_normalizes_by_trimming_and_lowercasing() -> None:
    assert Email.parse("  Ana@Mail.COM  ").value == "ana@mail.com"


@pytest.mark.parametrize(
    "raw",
    [
        "ana@mail.com",
        "a.b+tag@sub.example.co",
        "x@y.io",
        f"{MAX_LOCAL}@{MAX_DOMAIN}",  # 320 caracteres
    ],
)
def test_accepts_valid_emails(raw: str) -> None:
    assert Email.parse(raw).value == raw


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "ana",
        "ana@",
        "@mail.com",
        "ana@mail",
        "ana@@mail.com",
        "ana@mail@x.com",
        "an a@mail.com",
        "ana\t@mail.com",
        "ana@mail..com",
        "ana@.mail.com",
        "ana@mail.com.",
        "ana@mail.c",
        f"{MAX_LOCAL}a@mail.com",  # parte local de 65
        f"{MAX_LOCAL}@b{MAX_DOMAIN}",  # 321 caracteres
    ],
)
def test_rejects_invalid_emails(raw: str) -> None:
    with pytest.raises(InvalidUserData) as error:
        Email.parse(raw)

    assert error.value.details is not None
    assert set(error.value.details) == {"email"}


def test_equality_is_by_normalized_value() -> None:
    assert Email.parse("Ana@Mail.com") == Email.parse("ana@mail.com")


def test_is_immutable() -> None:
    email = Email.parse("ana@mail.com")

    with pytest.raises(AttributeError):
        email.value = "otro@mail.com"  # type: ignore[misc]
