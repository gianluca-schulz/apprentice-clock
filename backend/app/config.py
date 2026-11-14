from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str
    secret_key: str
    token_expiration_days: int


class AppState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    settings: Settings
    session_factory: async_sessionmaker[AsyncSession]
    engine: AsyncEngine
