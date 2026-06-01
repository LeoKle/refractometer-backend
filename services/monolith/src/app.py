from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from containers.container import DependencyContainer
from controllers.database import (
    image_controller,
    simulation_queue_controller,
    simulation_results_controller,
)
from router import root_api_router
from settings import config

container = DependencyContainer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    container.init_resources()
    container.wire(
        modules=[
            image_controller,
            simulation_queue_controller,
            simulation_results_controller,
        ]
    )

    handler = container.simulation_handler()
    handler.start()

    yield

    handler.stop()

    container.shutdown_resources()


app = FastAPI(title="Refractometer Backend", version=config.VERSION, lifespan=lifespan)

app.include_router(root_api_router)


@app.get("/")
async def redirect_api_docs():
    return RedirectResponse(url="/docs")
