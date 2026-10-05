"""Value object PersonName: reglas de nombres y apellidos (FR-006, spec/domain/user.md)."""

import pytest

from app.domain.errors import InvalidUserData
from app.domain.value_objects import PersonName


@pytest.mark.parametrize(
    "raw",
    ["Ana", "José", "Ñandú", "O'Connor", "Ana-María", "María José", "Müller", "a", "a" * 30],
)
def test_accepts_valid_names(raw: str) -> None:
    assert PersonName.parse(raw, field="name").value == raw


def test_trims_before_validating_length() -> None:
    assert PersonName.parse("  " + "a" * 30 + "  ", field="name").value == "a" * 30


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "a" * 31,
        "-Ana",
        "'Ana",
        "Ana2",
        "123",
        "Ana!",
        "Ana_María",
        "Ana\tMaría",
    ],
)
def test_rejects_invalid_names(raw: str) -> None:
    with pytest.raises(InvalidUserData) as error:
        PersonName.parse(raw, field="name")

    assert error.value.details is not None
    assert set(error.value.details) == {"name"}


def test_error_details_use_the_given_field() -> None:
    with pytest.raises(InvalidUserData) as error:
        PersonName.parse("", field="lastname")

    assert error.value.details is not None
    assert set(error.value.details) == {"lastname"}


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_optional_blank_is_none(raw: str | None) -> None:
    assert PersonName.parse_optional(raw, field="second_lastname") is None


def test_optional_value_is_validated() -> None:
    assert PersonName.parse_optional(" Pérez ", field="second_lastname") == PersonName.parse(
        "Pérez", field="second_lastname"
    )
    with pytest.raises(InvalidUserData):
        PersonName.parse_optional("P3rez", field="second_lastname")


def test_is_immutable() -> None:
    name = PersonName.parse("Ana", field="name")

    with pytest.raises(AttributeError):
        name.value = "Eva"  # type: ignore[misc]
