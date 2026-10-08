from fastapi import APIRouter

from api.controllers.v1 import simulation_controller

root_api_router = APIRouter(prefix="/api")

root_api_router.include_router(simulation_controller.router, tags=["Simulation Results"])
