from controllers.database import image, sample, simulation_queue, simulation_results
from fastapi import APIRouter
from controllers.app import meta
from controllers.database import (
    spectrum,
)

root_api_router = APIRouter(prefix="/api")

root_api_router.include_router(meta.router, tags=["meta"])
root_api_router.include_router(spectrum.router, tags=["spectrum"])
root_api_router.include_router(sample.router, tags=["sample"])
root_api_router.include_router(simulation_results.router, tags=["simulation_results"])
root_api_router.include_router(simulation_queue.router, tags=["simulation_queue"])
root_api_router.include_router(image.router, tags=["image"])
