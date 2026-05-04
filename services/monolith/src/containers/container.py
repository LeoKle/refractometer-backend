from dependency_injector import containers, providers

from containers.mongo_container import MongoContainer
from modules.app.simulation_handler import SimulationHandler
from modules.mongoDB.services.image_service import ImageService
from modules.mongoDB.services.sample_service import SampleService
from modules.mongoDB.services.simulation_queue_service import SimulationQueueService
from modules.mongoDB.services.simulation_result_service import SimulationResultService
from modules.mongoDB.services.spectrum_service import SpectrumService
from modules.simulation.simulation import Simulation
from settings import Settings


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_pydantic(Settings())

    mongo_container = providers.Container(MongoContainer, config=config)

    spectrum_service = providers.Factory(
        SpectrumService, db=mongo_container.mongo_database, collection_name="spectrums"
    )

    sample_service = providers.Factory(
        SampleService, db=mongo_container.mongo_database, collection_name="samples"
    )

    sim_results_service = providers.Factory(
        SimulationResultService,
        db=mongo_container.mongo_database,
        collection_name="simulation-results",
    )

    sim_queue_service = providers.Factory(
        SimulationQueueService,
        db=mongo_container.mongo_database,
        collection_name="simulation-queue",
    )

    image_service = providers.Factory(
        ImageService,
        db=mongo_container.mongo_database,
    )

    simulation = providers.Factory(Simulation)
    simulation_handler = providers.Singleton(
        SimulationHandler,
        simulation=simulation,
        simulation_queue_service=sim_queue_service,
        image_service=image_service,
        simulation_result_service=sim_results_service,
    )
