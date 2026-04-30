from abc import ABC, abstractmethod

from custom_types.simulation_result import SimulationResult


class ISimulationResultService(ABC):
    @abstractmethod
    def get_results(self) -> list[SimulationResult]:
        """Returns all results"""
        pass

    @abstractmethod
    def load_result(self, result_id: str) -> SimulationResult | None:
        pass

    @abstractmethod
    def save_result(self, result: SimulationResult):
        pass

    @abstractmethod
    def update_result(self, result: SimulationResult):
        pass

    @abstractmethod
    def delete_result(self, result_id: str):
        pass
