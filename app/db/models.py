from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, String

from .database import Base


class TaskDB(Base):
    """Database model for tasks."""

    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(16), nullable=False, default="todo", index=True)
    owner_id = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    due_date = Column(Date, nullable=True)
