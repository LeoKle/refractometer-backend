from abc import ABC, abstractmethod

from models.queue_element import QueueElement


class QueueServiceInterface(ABC):
    @abstractmethod
    def get_queued_simulations(self) -> list[QueueElement]: ...

    @abstractmethod
    def load_queued_simulation(self, queue_id: str) -> QueueElement | None: ...

    @abstractmethod
    def save_queued_simulation(self, queued_element: QueueElement): ...

    @abstractmethod
    def update_queued_simulation(self, queued_element: QueueElement): ...

    @abstractmethod
    def delete_queued_simulation(self, queue_id: str): ...

    @abstractmethod
    def claim_next_simulation(self): ...
