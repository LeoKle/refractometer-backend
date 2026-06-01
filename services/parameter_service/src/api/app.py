from fastapi import FastAPI

from api.controllers.v1 import sample_controller, spectrum_controller
from api.router import root_api_router
from containers.container import DependencyContainer

app = FastAPI(title="Refractometer Parameter Service")

container = DependencyContainer()

container.wire(modules=[sample_controller, spectrum_controller])

app.include_router(root_api_router)
