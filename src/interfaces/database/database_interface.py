from abc import ABC, abstractmethod

from backend.src.interfaces.database.services.sample_service_interface import ISampleService
from .services.spectrum_service_interface import ISpectrumService
from .services.simulation_result_service_interface import ISimulationResultService
from .services.simulation_queue_service_interface import ISimulationQueueService
from .services.image_service_interface import IImageService


class IDatabase(ABC):
    @abstractmethod
    def spectrum_service(self) -> ISpectrumService:
        pass

    @abstractmethod
    def sample_service(self) -> ISampleService:
        pass

    @abstractmethod
    def simulation_result_service(self) -> ISimulationResultService:
        pass

    @abstractmethod
    def simulation_queue_service(self) -> ISimulationQueueService:
        pass

    @abstractmethod
    def image_service(self) -> IImageService:
        pass
