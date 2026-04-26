from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from backend.src.config import config
from backend.src.router import root_api_router

app = FastAPI(title="Refractometer Backend", version=config.VERSION)

app.include_router(root_api_router)


@app.get("/")
async def redirect_api_docs():
    return RedirectResponse(url="/docs")
