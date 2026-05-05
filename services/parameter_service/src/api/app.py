from fastapi import FastAPI

from api.router import root_api_router
from containers.container import DependencyContainer

app = FastAPI(title="Refractometer Parameter Service")

container = DependencyContainer()

container.wire(modules=[])

app.include_router(root_api_router)
