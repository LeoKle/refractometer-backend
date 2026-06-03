from fastapi import FastAPI

from api.controllers import image_controller
from containers.container import DependencyContainer

app = FastAPI(title="Refractometer Image Service")

app.include_router(image_controller.router)

container = DependencyContainer()

container.wire(modules=[image_controller])
