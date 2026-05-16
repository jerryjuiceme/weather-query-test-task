"""Onupdate server default function

Revision ID: 9f4a03477b42
Revises: 30f69cbb29e6
Create Date: 2026-05-16 19:04:46.842714

"""

from typing import Sequence, Union
from pathlib import Path
from alembic import op, context

# revision identifiers, used by Alembic.
revision: str = "9f4a03477b42"
down_revision: Union[str, Sequence[str], None] = "30f69cbb29e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


on_update = (
    Path(
        context.config.get_section_option(  # type: ignore
            "extra",
            "functions.dir",
        )
    )
    / "on_update"
)


def upgrade() -> None:
    op.execute((on_update / "upgrade.sql").read_text())


def downgrade() -> None:
    op.execute((on_update / "downgrade.sql").read_text())
