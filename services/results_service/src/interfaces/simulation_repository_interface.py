from abc import ABC, abstractmethod

from models.simulation_result import SimulationResult


class SimulationResultRepositoryInterface(ABC):
    @abstractmethod
    def get_results(self) -> list[SimulationResult]: ...

    @abstractmethod
    def load_result(self, result_id: str) -> SimulationResult | None: ...

    @abstractmethod
    def save_result(self, result: SimulationResult) -> SimulationResult: ...

    @abstractmethod
    def update_result(self, result: SimulationResult) -> SimulationResult: ...

    @abstractmethod
    def delete_result(self, result_id: str) -> bool: ...
