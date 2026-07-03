from fastapi import FastAPI

from api import queue_controller
from container import DependencyContainer

container = DependencyContainer()
container.wire(
    modules=[
        queue_controller,
    ]
)
app = FastAPI(title="Refractometer Queue Service")

app.include_router(queue_controller.router)
