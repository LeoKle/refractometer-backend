from abc import ABC, abstractmethod

from custom_types.simulation_queue import SimulationQueueElement


class QueueServiceInterface(ABC):
    @abstractmethod
    def claim_element(self) -> SimulationQueueElement | None: ...

    @abstractmethod
    def delete_queued_element(self, queue_id: str) -> bool: ...
