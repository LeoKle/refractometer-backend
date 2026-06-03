from fastapi import FastAPI

from containers.container import DependencyContainer

app = FastAPI(title="Refractometer Image Service")

container = DependencyContainer()

container.wire(modules=[])
