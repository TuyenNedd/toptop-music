"""initial

Revision ID: 3514a6f0357f
Revises:
Create Date: 2026-03-27 08:29:46.945566

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "3514a6f0357f"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
