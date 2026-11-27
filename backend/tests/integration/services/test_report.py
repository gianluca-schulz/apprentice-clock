import datetime
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.report import Report
from app.schemas.report import ReportRequest
from app.services.report import (
    ReportAlreadyExistsError,
    ReportNotFoundError,
    create_report,
    get_owned_report,
    list_reports,
)

REQUEST_2026 = ReportRequest(date=datetime.date(2026, 11, 26), title="testtitle", description="testdescription")


REQUEST_2025 = ReportRequest(date=datetime.date(2025, 11, 26), title="testtitle", description="testdescription")


REQUEST_2027 = ReportRequest(date=datetime.date(2027, 11, 26), title="testtitle", description="testdescription")


async def test_report_saved_and_returned(session, session_factory, saved_user):
    await create_report(session=session, body=REQUEST_2026, user_id=saved_user.id)
    async with session_factory() as read_session:
        saved_report = await read_session.scalar(
            select(Report).where(Report.user_id == saved_user.id, Report.date == REQUEST_2026.date)
        )
    assert saved_report is not None
    assert saved_report.user_id == saved_user.id
    assert saved_report.date == REQUEST_2026.date
    assert saved_report.title == REQUEST_2026.title
    assert saved_report.description == REQUEST_2026.description


async def test_same_user_same_date_raises_report_already_exists(session, saved_user):
    await create_report(session=session, body=REQUEST_2026, user_id=saved_user.id)
    with pytest.raises(ReportAlreadyExistsError):
        await create_report(session=session, body=REQUEST_2026, user_id=saved_user.id)


async def test_two_user_same_date_works(session, saved_user, second_saved_user, session_factory):
    await create_report(session=session, body=REQUEST_2026, user_id=saved_user.id)
    await create_report(session=session, body=REQUEST_2026, user_id=second_saved_user.id)
    async with session_factory() as read_session:
        saved_report = await read_session.scalar(
            select(Report).where(Report.user_id == saved_user.id, Report.date == REQUEST_2026.date)
        )
        second_saved_report = await read_session.scalar(
            select(Report).where(Report.user_id == second_saved_user.id, Report.date == REQUEST_2026.date)
        )
    assert saved_report is not None
    assert second_saved_report is not None
    assert saved_report.date == second_saved_report.date
    assert saved_report.date == REQUEST_2026.date
    assert saved_report.user_id == saved_user.id
    assert second_saved_report.user_id == second_saved_user.id


async def test_unknown_user_raises_integrity_error_and_not_report_already_exists(session):
    with pytest.raises(IntegrityError, match="reports_user_id_fkey"):
        await create_report(session=session, body=REQUEST_2026, user_id=uuid4())


async def test_user_without_reports_returns_empty_list(session, saved_user):
    reportlist = await list_reports(session=session, user_id=saved_user.id)
    assert len(reportlist) == 0


async def test_reports_return_ordered(session, session_factory, saved_user):
    await create_report(session=session, body=REQUEST_2026, user_id=saved_user.id)
    await create_report(session=session, body=REQUEST_2025, user_id=saved_user.id)
    await create_report(session=session, body=REQUEST_2027, user_id=saved_user.id)
    async with session_factory() as list_session:
        reportlist = await list_reports(session=list_session, user_id=saved_user.id)
        assert len(reportlist) == 3
        assert reportlist[0].date == REQUEST_2027.date
        assert reportlist[1].date == REQUEST_2026.date
        assert reportlist[2].date == REQUEST_2025.date


async def test_list_contains_only_own_reports(session, session_factory, saved_user, second_saved_user):
    await create_report(session=session, body=REQUEST_2026, user_id=saved_user.id)
    await create_report(session=session, body=REQUEST_2025, user_id=second_saved_user.id)
    async with session_factory() as list_session:
        reportlist = await list_reports(session=list_session, user_id=saved_user.id)
        assert len(reportlist) == 1
        assert reportlist[0].date == REQUEST_2026.date
        assert reportlist[0].user_id == saved_user.id


async def test_owner_gets_the_report(session_factory, saved_user, saved_report):
    async with session_factory() as report_session:
        report = await get_owned_report(session=report_session, user_id=saved_user.id, report_id=saved_report.id)
    assert report.date == saved_report.date
    assert report.user_id == saved_user.id
    assert report.id == saved_report.id


async def test_other_user_gets_report_not_found(session_factory, second_saved_user, saved_report):
    async with session_factory() as report_session:
        with pytest.raises(ReportNotFoundError):
            await get_owned_report(session=report_session, user_id=second_saved_user.id, report_id=saved_report.id)


async def test_unknown_report_id_gets_report_not_found(session_factory, saved_user, saved_report):
    async with session_factory() as report_session:
        with pytest.raises(ReportNotFoundError):
            await get_owned_report(session=report_session, user_id=saved_user.id, report_id=uuid4())
