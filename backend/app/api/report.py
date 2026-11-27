from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.dependencies.auth import CurrentUser
from app.dependencies.database import CurrentSession
from app.schemas.report import ReportRequest, ReportResponse
from app.services.report import (
    ReportAlreadyExistsError,
    ReportNotFoundError,
    create_report,
    delete_report,
    get_owned_report,
    list_reports,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_report(session: CurrentSession, body: ReportRequest, user: CurrentUser) -> ReportResponse:
    try:
        report = await create_report(session=session, body=body, user_id=user.id)
    except ReportAlreadyExistsError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="report for this date already exists")
    return ReportResponse.model_validate(report)


@router.get("", status_code=status.HTTP_200_OK)
async def get_reports(session: CurrentSession, user: CurrentUser) -> list[ReportResponse]:
    report_list = await list_reports(session=session, user_id=user.id)
    return [ReportResponse.model_validate(report) for report in report_list]


@router.get("/{report_id}", status_code=status.HTTP_200_OK)
async def get_single_report(session: CurrentSession, user: CurrentUser, report_id: UUID) -> ReportResponse:
    try:
        report = await get_owned_report(session=session, user_id=user.id, report_id=report_id)
    except ReportNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="report was not found")
    return ReportResponse.model_validate(report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_report(session: CurrentSession, user: CurrentUser, report_id: UUID) -> None:
    try:
        await delete_report(session=session, user_id=user.id, report_id=report_id)
    except ReportNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="report was not found")
