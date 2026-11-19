from fastapi import APIRouter
from sqlalchemy import text

from app.dependencies.database import CurrentSession

router = APIRouter(tags=["health"])


@router.get("/health")
async def get_health(session: CurrentSession) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {"status": "ok"}
