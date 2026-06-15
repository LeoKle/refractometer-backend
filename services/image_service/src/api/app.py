from fastapi import FastAPI

from api.controllers import image_controller
from containers.container import DependencyContainer
from settings import Settings

app = FastAPI(title="Refractometer Image Service")
app.include_router(image_controller.router)

container = DependencyContainer()
container.wire(modules=[image_controller])

settings = Settings()
if settings.ENABLE_PACT_STATES:
    from api.controllers.pact_states_controller import router as pact_states_router

    app.include_router(pact_states_router)
    container.wire(modules=["api.controllers.pact_states_controller"])
