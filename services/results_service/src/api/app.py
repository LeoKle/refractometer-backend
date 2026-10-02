from fastapi import FastAPI

from api.router import root_api_router

app = FastAPI(title="Refractometer Results Service")

app.include_router(root_api_router)
