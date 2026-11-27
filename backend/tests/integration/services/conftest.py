import datetime

import pytest

from app.models.report import Report
from app.schemas.auth import RegisterRequest
from app.services.auth import register_user


@pytest.fixture()
async def registered_user_data(session) -> RegisterRequest:
    body = RegisterRequest(
        first_name="Testuser", last_name="lastnameuser", password="testpassword", email="test@user.de"
    )
    await register_user(session=session, body=body)
    return body


@pytest.fixture()
async def saved_report(saved_user, session_factory) -> Report:
    report = Report(
        user_id=saved_user.id, date=datetime.date(2026, 11, 26), title="testtitle", description="testdescription"
    )
    async with session_factory() as session:
        session.add(report)
        await session.commit()
    return report
