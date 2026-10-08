from fastapi import APIRouter

from controllers.app import meta

root_api_router = APIRouter(prefix="/api")

root_api_router.include_router(meta.router, tags=["meta"])
