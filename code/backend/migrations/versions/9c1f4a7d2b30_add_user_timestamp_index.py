from collections.abc import Sequence

from alembic import op

revision: str = "9c1f4a7d2b30"
down_revision: str | None = "2354e71bbed1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_energy_data_user_id_timestamp",
        "energy_data",
        ["user_id", "timestamp"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_energy_data_user_id_timestamp", table_name="energy_data")
