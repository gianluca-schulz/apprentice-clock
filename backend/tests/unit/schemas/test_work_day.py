from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.work_day import ClockOutRequest


def test_clock_out_left_out():
    request = ClockOutRequest(report="testreport")
    assert request.clock_out is None


def test_clock_out_is_none():
    request = ClockOutRequest(report="testreport", clock_out=None)
    assert request.clock_out is None


def test_time_in_past_is_valid():
    testtime = datetime.now(UTC) - timedelta(hours=1)
    request = ClockOutRequest(report="testreport", clock_out=testtime)
    assert request.clock_out == testtime


def test_spaces_around_report():
    testreport = "    test    "
    request = ClockOutRequest(report=testreport)
    assert request.report == "test"


@pytest.mark.parametrize(
    ("report", "clock_out", "field"),
    [
        ("testreport", datetime.now(UTC) + timedelta(hours=1), "clock_out"),
        ("testreport", datetime(2026, 11, 24, 17, 0), "clock_out"),
        ("", datetime.now(UTC) - timedelta(hours=1), "report"),
        ("          ", datetime.now(UTC) - timedelta(hours=1), "report"),
    ],
)
def test_clock_out_request_invalid(report, clock_out, field):
    with pytest.raises(ValidationError) as excinfo:
        ClockOutRequest(report=report, clock_out=clock_out)
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"][0] == field
