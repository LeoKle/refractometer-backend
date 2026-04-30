from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from containers.container import DependencyContainer
from settings import config
from router import root_api_router
from controllers.database import (
    image_controller,
    sample,
    simulation_queue_controller,
    simulation_results,
    spectrum,
)

app = FastAPI(title="Refractometer Backend", version=config.VERSION)

app.include_router(root_api_router)


@app.get("/")
async def redirect_api_docs():
    return RedirectResponse(url="/docs")


container = DependencyContainer()
container.wire(
    modules=[
        image_controller,
        sample,
        simulation_queue_controller,
        simulation_results,
        spectrum,
    ]
)
