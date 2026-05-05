from fastapi import FastAPI

from containers.container import DependencyContainer

app = FastAPI(title="Refractometer Parameter Service")

container = DependencyContainer()

container.wire(modules=[])
