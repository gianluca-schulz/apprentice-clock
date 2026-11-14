from app.config import Settings
from app.setup import create_app

settings = Settings()
app = create_app(settings)
