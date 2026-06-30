"""add leads.resume_text

Stores the text extracted from the resume PDF (pypdf), passed to the LLM and
kept for reference/search.

Revision ID: 0006_lead_resume_text
Revises: 0005_lead_profile_score
Create Date: 2026-06-30
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_lead_resume_text"
down_revision: Union[str, None] = "0005_lead_profile_score"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("resume_text", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("leads", "resume_text")
