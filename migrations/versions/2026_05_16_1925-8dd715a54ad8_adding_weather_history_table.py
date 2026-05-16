"""Adding weather history table

Revision ID: 8dd715a54ad8
Revises: 01967787f032
Create Date: 2026-05-16 19:25:34.390172

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8dd715a54ad8"
down_revision: Union[str, Sequence[str], None] = "01967787f032"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "weather_history",
        sa.Column("city_name", sa.String(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("humidity", sa.Integer(), nullable=False),
        sa.Column("units", sa.String(length=10), nullable=False),
        sa.Column("is_from_cache", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v7()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_weather_history_user_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_weather_history")),
    )
    op.create_index(
        op.f("ix_weather_history_city_name"),
        "weather_history",
        ["city_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_weather_history_created_at"),
        "weather_history",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_weather_history_created_at"), table_name="weather_history")
    op.drop_index(op.f("ix_weather_history_city_name"), table_name="weather_history")
    op.drop_table("weather_history")
