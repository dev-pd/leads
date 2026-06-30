"""Data-access layer for leads. The only place that issues lead DB queries."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.lead import Lead


class LeadRepository:
    def __init__(self, db: Session):
        self._db = db

    def add(self, lead: Lead) -> Lead:
        """Stage a new lead and flush so its generated id is available."""
        self._db.add(lead)
        self._db.flush()
        return lead

    def commit(self, lead: Lead) -> Lead:
        self._db.commit()
        self._db.refresh(lead)
        return lead

    def get(self, lead_id: str) -> Lead | None:
        return self._db.get(Lead, lead_id)

    def get_by_email(self, email: str) -> Lead | None:
        return self._db.scalar(select(Lead).where(Lead.email == email))

    def list(self) -> list[Lead]:
        return list(self._db.scalars(select(Lead).order_by(Lead.created_at.desc())))

    def count(self) -> int:
        return self._db.scalar(select(func.count()).select_from(Lead)) or 0
