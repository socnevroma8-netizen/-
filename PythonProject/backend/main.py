from fastapi import FastAPI

from .services.api import router as api_router
from .services.admin_api import router as admin_router


app = FastAPI(title="Schedule API")

app.include_router(api_router)
app.include_router(admin_router)