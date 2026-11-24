from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, StringConstraints, field_validator

ReportString = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]


class ClockOutRequest(BaseModel):
    report: ReportString
    clock_out: AwareDatetime | None = None

    @field_validator("clock_out")
    @classmethod
    def ensure_clock_out_not_in_future(cls, clock_out: AwareDatetime | None) -> AwareDatetime | None:
        if clock_out is not None and clock_out > datetime.now(UTC):
            raise ValueError("Clock out time cant be in the future")
        return clock_out


class WorkDayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    clock_in: AwareDatetime
    clock_out: AwareDatetime | None
    report: str | None
