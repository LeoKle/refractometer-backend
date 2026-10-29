from fastapi import FastAPI

from api.controllers import image_controller
from api.middleware.correlation_middleware import CorrelationIdMiddleware
from api.v2 import image_controller as image_controller_v2
from containers.container import DependencyContainer
from log import setup_logging
from settings import Settings

setup_logging()
app = FastAPI(title="Refractometer Image Service")
app.add_middleware(CorrelationIdMiddleware)
app.include_router(image_controller.router)
app.include_router(image_controller_v2.image_v2_router)

container = DependencyContainer()
container.wire(modules=[image_controller, image_controller_v2])

settings = Settings()
if settings.ENABLE_PACT_STATES:
    from api.controllers.pact_states_controller import router as pact_states_router

    app.include_router(pact_states_router)
    container.wire(modules=["api.controllers.pact_states_controller"])
