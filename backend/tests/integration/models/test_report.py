import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.report import Report

FIXED_DATE = datetime.date(2026, 11, 25)


async def test_saved_report_can_be_read_back(session_factory, saved_user):
    testreport = Report(
        user_id=saved_user.id,
        date=FIXED_DATE,
        title="testtitle",
        description="test description of my first day at work",
    )
    async with session_factory() as session:
        session.add(testreport)
        await session.commit()
    async with session_factory() as session:
        db_report = await session.get(Report, testreport.id)
    assert db_report is not None
    assert db_report.title == "testtitle"
    assert db_report.date == FIXED_DATE
    assert db_report.user_id == saved_user.id


async def test_duplicate_date_throws_error(session_factory, saved_user):
    testreport = Report(
        user_id=saved_user.id,
        date=FIXED_DATE,
        title="testtitle",
        description="test description of my first day at work",
    )
    async with session_factory() as session:
        session.add(testreport)
        await session.commit()
    same_date_report = Report(
        user_id=saved_user.id, date=FIXED_DATE, title="second_testtitle", description="duplicate date report"
    )
    async with session_factory() as session:
        session.add(same_date_report)
        with pytest.raises(IntegrityError, match="uq_reports_user_id_date"):
            await session.commit()


async def test_same_user_can_save_reports_for_different_dates(session_factory, saved_user):
    testreport = Report(
        user_id=saved_user.id,
        date=FIXED_DATE,
        title="testtitle",
        description="test description of my first day at work",
    )
    testreport2 = Report(
        user_id=saved_user.id,
        date=datetime.date(2026, 11, 24),
        title="secondtesttitle",
        description="test description of my second day at work",
    )
    async with session_factory() as session:
        session.add(testreport)
        session.add(testreport2)
        await session.commit()
    async with session_factory() as session:
        reports = (await session.scalars(select(Report).where(Report.user_id == saved_user.id))).all()
        assert len(reports) == 2
        assert {report.title for report in reports} == {"testtitle", "secondtesttitle"}
