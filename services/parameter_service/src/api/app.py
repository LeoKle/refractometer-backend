from fastapi import FastAPI

from api.controllers.v1 import sample_controller, spectrum_controller
from api.router import root_api_router
from containers.container import DependencyContainer
from settings import Settings

app = FastAPI(title="Refractometer Parameter Service")

container = DependencyContainer()

container.wire(modules=[sample_controller, spectrum_controller])

app.include_router(root_api_router)

settings = Settings()
if settings.ENABLE_PACT_STATES:
    from api.controllers.v1.pact_states_controller import router as pact_states_router

    app.include_router(pact_states_router)
    container.wire(modules=["api.controllers.v1.pact_states_controller"])
