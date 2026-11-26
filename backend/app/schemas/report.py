import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

TitleString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ReportRequest(BaseModel):
    date: datetime.date
    title: TitleString
    description: str = ""


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    date: datetime.date
    title: str
    description: str
