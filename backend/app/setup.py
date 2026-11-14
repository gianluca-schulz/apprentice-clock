from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.health import router
from app.config import AppState, Settings


def create_app(settings: Settings) -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = create_async_engine(settings.database_url)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        app.state = AppState(settings=settings, session_factory=session_factory, engine=engine)
        yield
        await engine.dispose()

    app = FastAPI(title="apprentice-clock", version="0.1.0", lifespan=lifespan)
    app.include_router(router, prefix="/api/v1")

    return app
