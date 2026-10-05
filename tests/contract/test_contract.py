"""La API cumple el contrato canónico spec/openapi/users-api.yaml (SC-002, Principio II)."""

from pathlib import Path

import pytest
import schemathesis
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
# GET/PUT/DELETE /users/{user_id} no figuran porque ya cumplen el contrato con
# 404 NOT_FOUND (respuesta documentada); su comportamiento real lo cubren T026/T030/T034.
PENDING = {
    "GET /users": "T028",
}

schema = schemathesis.pytest.from_fixture("contract_schema")


@schema.parametrize()
def test_api_conforms_to_contract(case: schemathesis.Case) -> None:
    task = PENDING.get(case.operation.label)
    if task is None:
        case.call_and_validate()
        return
    # Pendiente: la ruta no existe (404 NOT_FOUND) o existe solo con otros métodos
    # (405 METHOD_NOT_ALLOWED). En cuanto se implemente, hay que quitarla de PENDING para que
    # Schemathesis la valide (equivalente a un xfail estricto).
    response = case.call()
    not_implemented = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
    if not_implemented.get(response.status_code) == response.json().get("code"):
        pytest.xfail(f"{case.operation.label} pendiente de implementar ({task})")
    pytest.fail(f"{case.operation.label} ya está implementada: quítala de PENDING ({task})")
