from dependency_injector import containers, providers
from refractometer_common.queue import QueueClient
from refractometer_common.result import SimulationResultClient

from containers.mongo_container import MongoContainer
from modules.app.simulation_handler import SimulationHandler
from modules.simulation.mock_simulation import MockSimulation
from modules.simulation.simulation import Simulation
from services.image_service import ImageService
from settings import Settings


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_pydantic(Settings())

    mongo_container = providers.Container(MongoContainer, config=config)

    sim_result_client = providers.Factory(
        SimulationResultClient,
        base_url=config.SIM_RESULT_SERVICE_URL,
    )

    queue_client = providers.Factory(QueueClient, base_url=config.QUEUE_SERVICE_URL)

    image_service = providers.Factory(
        ImageService,
        base_url=config.IMAGE_SERVICE_URL,
    )

    simulation = providers.Selector(
        providers.Callable(
            lambda use_mock: "mock" if use_mock else "real",
            config.USE_MOCK_SIMULATION,
        ),
        mock=providers.Factory(MockSimulation),
        real=providers.Factory(Simulation),
    )

    simulation_handler = providers.Singleton(
        SimulationHandler,
        simulation=simulation,
        queue_client=queue_client,
        image_service=image_service,
        simulation_result_client=sim_result_client,
    )
