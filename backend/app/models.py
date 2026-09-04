from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class IssueRecord(Base):
    __tablename__ = "issues"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    github_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
    repo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    issue_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(40), default="other")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
