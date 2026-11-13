from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str

class AppState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    settings: Settings
    session_factory: async_sessionmaker[AsyncSession]
    engine: AsyncEngine 