"""add leads.resume_summary

Stores the AI-generated profile produced from the resume.

Revision ID: 0004_lead_resume_summary
Revises: 0003_lead_reached_out_at
Create Date: 2026-06-30
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_lead_resume_summary"
down_revision: Union[str, None] = "0003_lead_reached_out_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("resume_summary", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("leads", "resume_summary")
