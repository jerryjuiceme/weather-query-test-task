"""Adding auth tables and triggers

Revision ID: 01967787f032
Revises: 9f4a03477b42
Create Date: 2026-05-16 19:09:16.624537

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "01967787f032"
down_revision: Union[str, Sequence[str], None] = "9f4a03477b42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TRIGGER_SQL_USER = """
    CREATE TRIGGER update_updated_at_user
    BEFORE UPDATE ON "user"
    FOR EACH ROW EXECUTE PROCEDURE updated_at();
    """


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("preferred_username", sa.String(), nullable=True),
        sa.Column("given_name", sa.String(), nullable=True),
        sa.Column("family_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.execute(TRIGGER_SQL_USER)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP TRIGGER IF EXISTS update_updated_at_user ON "user";')
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
