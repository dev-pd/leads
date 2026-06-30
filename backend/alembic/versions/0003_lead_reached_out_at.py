"""add leads.reached_out_at

Records when a lead was marked REACHED_OUT, for the activity trail.

Revision ID: 0003_lead_reached_out_at
Revises: 0002_unique_lead_email
Create Date: 2026-06-30
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_lead_reached_out_at"
down_revision: Union[str, None] = "0002_unique_lead_email"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column("reached_out_at", sa.DateTime(timezone=True), nullable=True),
    )
    # Backfill existing reached-out leads so their trail isn't empty.
    op.execute(
        "UPDATE leads SET reached_out_at = updated_at WHERE state = 'REACHED_OUT'"
    )


def downgrade() -> None:
    op.drop_column("leads", "reached_out_at")
