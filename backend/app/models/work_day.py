from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class WorkDay(Base):
    __tablename__ = "work_days"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    clock_in: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    clock_out: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    work_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=utc_now, default=utc_now)
    report: Mapped[str | None] = mapped_column(Text)
    __table_args__ = ((UniqueConstraint("user_id", "work_date", name="uq_work_days_one_per_day_and_user")),)
