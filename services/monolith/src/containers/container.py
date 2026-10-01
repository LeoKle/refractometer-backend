from dependency_injector import containers, providers
from refractometer_common.queue import QueueClient

from containers.mongo_container import MongoContainer
from modules.app.simulation_handler import SimulationHandler
from modules.mongoDB.services.simulation_result_service import SimulationResultService
from modules.simulation.mock_simulation import MockSimulation
from modules.simulation.simulation import Simulation
from services.image_service import ImageService
from settings import Settings


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_pydantic(Settings())

    mongo_container = providers.Container(MongoContainer, config=config)

    sim_results_service = providers.Factory(
        SimulationResultService,
        db=mongo_container.mongo_database,
        collection_name="simulation-results",
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
        simulation_result_service=sim_results_service,
    )
