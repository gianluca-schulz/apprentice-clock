from fastapi import FastAPI

from app.api.health import router

app = FastAPI(title="apprentice-clock", version="0.1.0")

app.include_router(router, prefix="/api/v1")
