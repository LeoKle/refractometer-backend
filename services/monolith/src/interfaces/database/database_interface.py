from abc import ABC, abstractmethod

from .services.simulation_queue_service_interface import ISimulationQueueService
from .services.simulation_result_service_interface import ISimulationResultService


class IDatabase(ABC):
    @abstractmethod
    def simulation_result_service(self) -> ISimulationResultService:
        pass

    @abstractmethod
    def simulation_queue_service(self) -> ISimulationQueueService:
        pass
