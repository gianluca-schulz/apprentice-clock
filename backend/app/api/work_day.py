from fastapi import APIRouter, HTTPException, status

from app.dependencies.auth import CurrentUser
from app.dependencies.database import CurrentSession
from app.schemas.work_day import WorkDayResponse
from app.services.work_day import AlreadyClockedInError, OpenWorkDayError, clock_in

router = APIRouter(prefix="/work-days", tags=["work-days"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_work_day(session: CurrentSession, user: CurrentUser) -> WorkDayResponse:
    try:
        work_day = await clock_in(session=session, user_id=user.id)
    except AlreadyClockedInError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="user is already clocked-in for today")
    except OpenWorkDayError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="user has an open workday that needs to be closed first")
    return WorkDayResponse.model_validate(work_day)
