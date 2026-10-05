"""create users table

Revision ID: 5a2a164feec3
Revises:
Create Date: 2026-10-04 22:22:00

Tabla `users` según spec/data/schema.md (FR-004, NFR-006). Tabla nueva y vacía: los índices
se crean sin CONCURRENTLY; las migraciones posteriores siguen expand/contract (NFR-009).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5a2a164feec3"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Toda migración debe ser reversible (NFR-006) y seguir expand/contract (NFR-009).
def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("name", sa.String(30), nullable=False),
        sa.Column("lastname", sa.String(30), nullable=False),
        sa.Column("second_lastname", sa.String(30), nullable=True),
        sa.Column("status", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    # Unicidad case-insensitive y segura ante concurrencia (FR-004).
    op.create_index(
        "ux_users_email_lower",
        "users",
        [sa.text("lower(email)")],
        unique=True,
    )
    # Listado paginado de activos con orden estable (FR-001).
    op.create_index(
        "ix_users_status_created_at",
        "users",
        ["status", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_users_status_created_at", table_name="users")
    op.drop_index("ux_users_email_lower", table_name="users")
    op.drop_table("users")
