import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReportRequest(BaseModel):
    date: datetime.date
    title: str = ""
    description: str = ""


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    date: datetime.date
    title: str
    description: str
