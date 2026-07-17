from fastapi import APIRouter

from controllers.app import meta
from controllers.database import (
    simulation_results_controller,
)

root_api_router = APIRouter(prefix="/api")

root_api_router.include_router(meta.router, tags=["meta"])
root_api_router.include_router(simulation_results_controller.router, tags=["simulation_results"])
