from fastapi import FastAPI

from app.api.routes.geocode import router as geocode_router
from app.api.routes.health import router as health_router
from app.config import get_settings
from app.utils.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(geocode_router)
