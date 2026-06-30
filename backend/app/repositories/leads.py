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

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
        rating: str | None = None,
        sort: str = "recent",
    ) -> list[Lead]:
        stmt = select(Lead)
        if rating is not None:
            stmt = stmt.where(Lead.profile_rating == rating)
        if sort == "score":
            # Highest fit first; unscored leads sink to the bottom.
            stmt = stmt.order_by(
                Lead.profile_score.desc().nulls_last(), Lead.created_at.desc()
            )
        else:
            stmt = stmt.order_by(Lead.created_at.desc())
        stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self._db.scalars(stmt))

    def count(self, *, rating: str | None = None) -> int:
        stmt = select(func.count()).select_from(Lead)
        if rating is not None:
            stmt = stmt.where(Lead.profile_rating == rating)
        return self._db.scalar(stmt) or 0

    def state_counts(self) -> dict[str, int]:
        """Total leads per state across the whole table (for global KPIs)."""
        rows = self._db.execute(
            select(Lead.state, func.count()).group_by(Lead.state)
        ).all()
        return {state.value: count for state, count in rows}
