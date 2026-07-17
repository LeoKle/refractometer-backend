import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from api.middleware.correlation_middleware import CorrelationIdMiddleware
from containers.container import DependencyContainer
from controllers.database import (
    simulation_results_controller,
)
from log import setup_logging
from router import root_api_router
from settings import config

setup_logging()
container = DependencyContainer()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI app")
    container.init_resources()
    container.wire(
        modules=[
            simulation_results_controller,
        ]
    )

    handler = container.simulation_handler()
    handler.start()

    yield

    handler.stop()

    container.shutdown_resources()
    logger.info("Shutdown FastAPI app")


app = FastAPI(title="Refractometer Backend", version=config.VERSION, lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(root_api_router)


@app.get("/")
async def redirect_api_docs():
    return RedirectResponse(url="/docs")
