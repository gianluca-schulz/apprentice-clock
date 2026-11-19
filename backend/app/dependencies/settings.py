from typing import Annotated

from fastapi import Depends, Request

from app.config import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


CurrentSettings = Annotated[Settings, Depends(get_settings)]
