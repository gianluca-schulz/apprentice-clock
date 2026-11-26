import datetime

import pytest
from pydantic import ValidationError

from app.schemas.report import ReportRequest

FIXED_DATE = datetime.date(2026, 11, 25)


def test_valid_request_passes():
    request = ReportRequest(date=FIXED_DATE, title="testtitle", description="testdescription")
    assert request.date == FIXED_DATE
    assert request.title == "testtitle"
    assert request.description == "testdescription"


def test_missing_description_becomes_empty_space():
    request = ReportRequest(date=FIXED_DATE, title="testtitle")
    assert request.description == ""


def test_title_missing_becomes_empty_space():
    request = ReportRequest(date=FIXED_DATE)
    assert request.title == ""


@pytest.mark.parametrize(
    ("date"),
    [("fakedate"), ("25.11.2026"), ("2026-13-45")],
)
def test_invalid_date_gets_refused(date):
    with pytest.raises(ValidationError):
        ReportRequest(date=date, title="testtitle")


def test_missing_date_gets_refused():
    with pytest.raises(ValidationError):
        ReportRequest(title="testtitle")


def test_description_with_none_gets_refused():
    with pytest.raises(ValidationError):
        ReportRequest(date=FIXED_DATE, title="testtitle", description=None)
