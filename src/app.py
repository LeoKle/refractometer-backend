from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from config import config
from router import root_api_router

app = FastAPI(title="Refractometer Backend", version=config.VERSION)

app.include_router(root_api_router)


@app.get("/")
async def redirect_api_docs():
    return RedirectResponse(url="/docs")
