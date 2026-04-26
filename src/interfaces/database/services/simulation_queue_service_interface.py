from abc import ABC, abstractmethod
from typing import List

from custom_types.simulation_queue import SimulationQueueElement


class ISimulationQueueService(ABC):
    @abstractmethod
    def get_queued_simulations(self) -> List[SimulationQueueElement]:
        """Returns all queued simulations"""
        pass

    @abstractmethod
    def load_queued_simulation(self, queue_id: str) -> SimulationQueueElement | None:
        pass

    @abstractmethod
    def save_queued_simulation(self, queued_element: SimulationQueueElement):
        pass

    @abstractmethod
    def update_queued_simulation(self, queued_element: SimulationQueueElement):
        pass

    @abstractmethod
    def delete_queued_simulation(self, queue_id: str):
        pass

    @abstractmethod
    def find_next_simulation(self):
        pass
