"""Add UUID v7 function

Revision ID: 30f69cbb29e6
Revises:
Create Date: 2026-05-16 19:00:46.890057

"""

from typing import Sequence, Union
from pathlib import Path
from alembic import op, context

# revision identifiers, used by Alembic.
revision: str = "30f69cbb29e6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


uuid_v7_functions = (
    Path(
        context.config.get_section_option(  # type: ignore
            "extra",
            "functions.dir",
        )
    )
    / "uuid_v7"
)


def upgrade() -> None:
    """
    Upgrade schema.
    We create the uuid_v7 function
    """
    op.execute(
        (uuid_v7_functions / "upgrade.sql").read_text(),
    )


def downgrade() -> None:
    """
    Downgrade schema.
    We drop the uuid_v7 function
    """
    op.execute(
        (uuid_v7_functions / "downgrade.sql").read_text(),
    )
