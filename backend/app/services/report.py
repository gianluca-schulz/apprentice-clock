from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report
from app.schemas.report import ReportRequest


class ReportAlreadyExistsError(Exception):
    pass


UNIQUE_DATE_CONSTRAINT = "uq_reports_user_id_date"


async def create_report(session: AsyncSession, body: ReportRequest, user_id: UUID) -> Report:
    report = Report(user_id=user_id, date=body.date, title=body.title, description=body.description)

    session.add(report)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        if UNIQUE_DATE_CONSTRAINT in str(error):
            raise ReportAlreadyExistsError from error
        raise
    return report


async def list_reports(session: AsyncSession, user_id: UUID) -> list[Report]:
    query = select(Report).where(Report.user_id == user_id).order_by(Report.date.desc())
    result = await session.scalars(query)
    return list(result.all())
