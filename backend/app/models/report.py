import datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

UNIQUE_DATE_CONSTRAINT = "uq_reports_user_id_date"


class Report(Base):
    __tablename__ = "reports"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    date: Mapped[datetime.date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    __table_args__ = (UniqueConstraint("user_id", "date", name=UNIQUE_DATE_CONSTRAINT),)
