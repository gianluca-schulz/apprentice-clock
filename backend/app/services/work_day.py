from datetime import date, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import Date, cast, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.work_day import WorkDay

APP_TIMEZONE = ZoneInfo("Europe/Berlin")


class AlreadyClockedInError(Exception):
    pass


class OpenWorkDayError(Exception):
    pass


async def _has_open_work_day(session: AsyncSession, user_id: UUID) -> bool:
    query = select(WorkDay).where(WorkDay.user_id == user_id, WorkDay.clock_out.is_(None))
    found = await session.scalar(query)
    return found is not None


async def _has_clocked_in_today(session: AsyncSession, user_id: UUID) -> bool:
    day_in_berlin = cast(func.timezone(APP_TIMEZONE.key, WorkDay.clock_in), Date)
    query = select(WorkDay).where(WorkDay.user_id == user_id, day_in_berlin == _today_in_berlin())
    found = await session.scalar(query)
    return found is not None


def _today_in_berlin() -> date:
    return datetime.now(tz=APP_TIMEZONE).date()


async def clock_in(session: AsyncSession, user_id: UUID) -> WorkDay:
    if await _has_clocked_in_today(session=session, user_id=user_id):
        raise AlreadyClockedInError
    if await _has_open_work_day(session=session, user_id=user_id):
        raise OpenWorkDayError
    work_day = WorkDay(user_id=user_id)
    session.add(work_day)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise AlreadyClockedInError from None
    await session.refresh(work_day)
    return work_day
