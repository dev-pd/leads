"""enforce unique lead email

Removes any duplicate leads (keeping the earliest per email) and adds a unique
constraint so a prospect can only submit once.

Revision ID: 0002_unique_lead_email
Revises: 0001_initial
Create Date: 2026-06-30
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002_unique_lead_email"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop duplicates, keeping the earliest submission per email.
    op.execute(
        """
        DELETE FROM leads a
        USING leads b
        WHERE a.email = b.email
          AND (a.created_at, a.id) > (b.created_at, b.id)
        """
    )
    op.create_unique_constraint("uq_leads_email", "leads", ["email"])


def downgrade() -> None:
    op.drop_constraint("uq_leads_email", "leads", type_="unique")
