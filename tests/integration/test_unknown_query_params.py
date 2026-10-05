"""Parámetros de consulta no declarados: 422 en /users, ignorados en /health."""

from uuid import uuid4

import httpx
import pytest


@pytest.mark.parametrize(
    ("path", "params", "unknown"),
    [
        ("/users", {"limt": 10}, "limt"),
        ("/users", {"limit": 5, "page": 2}, "page"),
        (f"/users/{uuid4()}", {"x": 1}, "x"),
    ],
    ids=["typo", "mixed-with-known", "get-by-id"],
)
async def test_users_rejects_unknown_query_params(
    client: httpx.AsyncClient, path: str, params: dict[str, object], unknown: str
) -> None:
    response = await client.get(path, params=params)

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert unknown in response.json()["details"]


async def test_users_rejects_unknown_query_params_on_post(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/users",
        params={"debug": "1"},
        json={"email": "ana@mail.com", "name": "Ana", "lastname": "López"},
    )

    assert response.status_code == 422
    assert "debug" in response.json()["details"]


async def test_known_query_params_are_accepted(client: httpx.AsyncClient) -> None:
    response = await client.get("/users", params={"limit": 5, "offset": 0})

    assert response.status_code == 200


@pytest.mark.parametrize("path", ["/health/live", "/health/ready"])
async def test_health_ignores_unknown_query_params(client: httpx.AsyncClient, path: str) -> None:
    # Monitores y balanceadores pueden añadir parámetros anti-caché.
    response = await client.get(path, params={"_": "1696500000"})

    assert response.status_code == 200
