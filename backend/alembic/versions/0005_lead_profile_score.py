"""add lead profile scoring columns

Stores the AI fit score, rating, and structured assessment for each resume.

Revision ID: 0005_lead_profile_score
Revises: 0004_lead_resume_summary
Create Date: 2026-06-30
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_lead_profile_score"
down_revision: Union[str, None] = "0004_lead_resume_summary"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("profile_score", sa.Integer(), nullable=True))
    op.add_column("leads", sa.Column("profile_rating", sa.String(length=16), nullable=True))
    op.add_column("leads", sa.Column("profile_assessment", sa.Text(), nullable=True))
    op.create_index("ix_leads_profile_score", "leads", ["profile_score"])
    op.create_index("ix_leads_profile_rating", "leads", ["profile_rating"])


def downgrade() -> None:
    op.drop_index("ix_leads_profile_rating", table_name="leads")
    op.drop_index("ix_leads_profile_score", table_name="leads")
    op.drop_column("leads", "profile_assessment")
    op.drop_column("leads", "profile_rating")
    op.drop_column("leads", "profile_score")
