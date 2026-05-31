from fastapi import APIRouter

from api.controllers.v1 import sample_controller, spectrum_controller

root_api_router = APIRouter(prefix="/api")

root_api_router.include_router(sample_controller.router, tags=["sample"])
root_api_router.include_router(spectrum_controller.router, tags=["Spectrum"])
