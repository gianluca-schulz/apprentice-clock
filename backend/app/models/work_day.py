from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class WorkDay(Base):
    __tablename__ = "work_days"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    clock_in: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    clock_out: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=utc_now, default=utc_now)
    report: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        Index(
            "uq_work_days_one_per_day_and_user",
            "user_id",
            text("(date(clock_in AT TIME ZONE 'Europe/Berlin'))"),
            unique=True,
        ),
    )
