"""La API cumple el contrato canónico spec/openapi/users-api.yaml (SC-002, Principio II)."""

from pathlib import Path

import pytest
import schemathesis
from schemathesis.specs.openapi.checks import allow_header_conformance
from schemathesis.specs.openapi.schemas import OpenApiSchema

from app.config import Settings
from app.main import create_app

CONTRACT = Path(__file__).resolve().parents[2] / "spec" / "openapi" / "users-api.yaml"


@pytest.fixture(scope="session")
def contract_schema(migrated_database_url: str) -> OpenApiSchema:
    """Contrato canónico servido por la app real contra PostgreSQL migrado.

    Schemathesis arranca el lifespan de la app una vez y lo mantiene en su propio event loop.
    """
    schema = schemathesis.openapi.from_path(CONTRACT)
    schema.app = create_app(Settings(_env_file=None, database_url=migrated_database_url))
    return schema


# Operaciones aún no implementadas: rojo esperado (xfail estricto) hasta su tarea.
PENDING: dict[str, str] = {
    "PUT /users/{user_id}": "T032",
    "DELETE /users/{user_id}": "T035",
}

# Comprobaciones desactivadas temporalmente por depender de operaciones pendientes.
# GET /users/{user_id}: el 405 anuncia Allow: GET, pero el contrato declara GET, PUT y DELETE
# para esa ruta; se resuelve cuando existan PUT (T032) y DELETE (T035).
TEMPORARILY_EXCLUDED_CHECKS = {
    "GET /users/{user_id}": [allow_header_conformance],  # TODO(T035): quitar
}

schema = schemathesis.pytest.from_fixture("contract_schema")


@schema.parametrize()
def test_api_conforms_to_contract(case: schemathesis.Case) -> None:
    task = PENDING.get(case.operation.label)
    if task is None:
        case.call_and_validate(
            excluded_checks=TEMPORARILY_EXCLUDED_CHECKS.get(case.operation.label, [])
        )
        return
    # Pendiente: la ruta no existe (404 NOT_FOUND) o existe solo con otros métodos
    # (405 METHOD_NOT_ALLOWED). En cuanto se implemente, hay que quitarla de PENDING para que
    # Schemathesis la valide (equivalente a un xfail estricto).
    response = case.call()
    not_implemented = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
    if not_implemented.get(response.status_code) == response.json().get("code"):
        pytest.xfail(f"{case.operation.label} pendiente de implementar ({task})")
    pytest.fail(f"{case.operation.label} ya está implementada: quítala de PENDING ({task})")
