from datetime import UTC, datetime

from app.services.work_day import clock_in


async def test_user_can_clock_in_successfully(session, created_user):
    time_before = datetime.now(UTC)
    work_day = await clock_in(session=session, user_id=created_user.id)
    time_after = datetime.now(UTC)
    assert time_before <= work_day.clock_in <= time_after
    assert work_day.user_id == created_user.id
    assert work_day.report is None
    assert work_day.clock_out is None
