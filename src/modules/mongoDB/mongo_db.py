from enum import Enum
from pymongo import MongoClient

from backend.src.config import config

from backend.src.interfaces.database.database_interface import IDatabase
from backend.src.interfaces.database.services.sample_service_interface import ISampleService
from backend.src.interfaces.database.services.spectrum_service_interface import (
    ISpectrumService,
)
from backend.src.interfaces.database.services.simulation_result_service_interface import (
    ISimulationResultService,
)
from backend.src.interfaces.database.services.simulation_queue_service_interface import (
    ISimulationQueueService,
)
from backend.src.interfaces.database.services.image_service_interface import IImageService

from .services.spectrum_service import SpectrumService
from .services.sample_service import SampleService
from .services.simulation_result_service import SimulationResultService
from .services.simulation_queue_service import SimulationQueueService
from .services.image_service import ImageService


class Collections(Enum):
    SPECTRUMS = "spectrums"
    SAMPLES = "samples"
    SIMULATION_RESULTS = "simulation-results"
    SIMULATION_QUEUE = "simulation-queue"


class MongoDB(IDatabase):
    _spectrum_service_instance: ISpectrumService = None
    _sample_service_instance: ISampleService = None
    _simulation_result_service_instance: ISimulationResultService = None
    _simulation_queue_service_instance: ISimulationQueueService = None
    _image_service_instance: IImageService = None

    def __init__(self):
        self.client = MongoClient(config.MONGO_URI)
        self.db = self.client[config.MONGO_DB_NAME]

    def spectrum_service(self) -> ISpectrumService:
        if MongoDB._spectrum_service_instance is None:
            MongoDB._spectrum_service_instance = SpectrumService(
                self.db, Collections.SPECTRUMS.value
            )
        return MongoDB._spectrum_service_instance

    def sample_service(self) -> ISampleService:
        if MongoDB._sample_service_instance is None:
            MongoDB._sample_service_instance = SampleService(
                self.db, Collections.SAMPLES.value
            )
        return MongoDB._sample_service_instance

    def simulation_result_service(self) -> ISimulationResultService:
        if MongoDB._simulation_result_service_instance is None:
            MongoDB._simulation_result_service_instance = SimulationResultService(
                self.db,
                Collections.SIMULATION_RESULTS.value,
            )
        return MongoDB._simulation_result_service_instance

    def simulation_queue_service(self) -> ISimulationQueueService:
        if MongoDB._simulation_queue_service_instance is None:
            MongoDB._simulation_queue_service_instance = SimulationQueueService(
                self.db,
                Collections.SIMULATION_QUEUE.value,
            )
        return MongoDB._simulation_queue_service_instance

    def image_service(self) -> IImageService:
        if MongoDB._image_service_instance is None:
            MongoDB._image_service_instance = ImageService(
                self.db,
            )
        return MongoDB._image_service_instance
