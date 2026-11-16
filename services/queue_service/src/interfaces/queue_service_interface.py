from abc import ABC, abstractmethod

from models.queue_element import QueueElement


class QueueServiceInterface(ABC):
    @abstractmethod
    def get_queued_simulations(self) -> list[QueueElement]: ...

    @abstractmethod
    def load_queued_simulation(self, queue_id: str) -> QueueElement | None: ...

    @abstractmethod
    def save_queued_simulation(self, queued_element: QueueElement) -> QueueElement: ...

    @abstractmethod
    def update_queued_simulation(self, queued_element: QueueElement): ...

    @abstractmethod
    def delete_queued_simulation(self, queue_id: str): ...

    @abstractmethod
    def claim_next_simulation(self): ...

    @abstractmethod
    def release_simulation(self, queue_id: str, error: str | None = None) -> bool:
        """Hand a claimed element back to the queue (saga compensation of the claim).

        Stores the error that caused the release. Returns False if the element does
        not exist. Releasing twice has the same effect as releasing once.
        """

    @abstractmethod
    def complete_simulation(sel, queue_id: str) -> None: ...
