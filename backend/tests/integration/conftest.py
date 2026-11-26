from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.community.postgres import PostgresContainer

from app.config import Settings
from app.models.base import Base
from app.models.user import User
from app.setup import create_app


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    with PostgresContainer("postgres:17-alpine", driver="psycopg") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture(scope="session")
def app_settings(database_url: str) -> Settings:
    return Settings(
        database_url=database_url,
        secret_key="testkeyhastbelongersowemakeitwaylongerthanbefore",
        token_expiration_days=1,
    )


@pytest.fixture(scope="session")
def app(app_settings) -> FastAPI:
    return create_app(settings=app_settings)


@pytest.fixture()
async def engine(app_settings) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(app_settings.database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture()
def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture()
async def session(session_factory) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


@pytest.fixture()
def client(app, engine) -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture()
async def saved_user(session_factory) -> User:
    user = User(first_name="testname", last_name="testlastname", email="test@email.com", password_hash="passwordhash")
    async with session_factory() as session:
        session.add(user)
        await session.commit()
    return user


@pytest.fixture()
async def second_saved_user(session_factory) -> User:
    user = User(
        first_name="secondtestname",
        last_name="secondtestlastname",
        email="secondtest@email.com",
        password_hash="secondpasswordhash",
    )
    async with session_factory() as session:
        session.add(user)
        await session.commit()
    return user
