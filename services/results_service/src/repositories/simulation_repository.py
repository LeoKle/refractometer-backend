from pymongo.collection import Collection

from interfaces.simulation_repository_interface import SimulationResultRepositoryInterface
from models.simulation_result import SimulationResult


class SimulationResultRepository(SimulationResultRepositoryInterface):
    def __init__(self, collection: Collection):
        self.collection = collection

    @staticmethod
    def _to_domain(document: dict) -> SimulationResult:
        return SimulationResult(**document)

    @staticmethod
    def _to_collection(result: SimulationResult) -> dict:
        return result.model_dump(mode="json")

    def get_results(self) -> list[SimulationResult]:
        results = self.collection.find({})
        return [self._to_domain(result) for result in results]

    def load_result(self, result_id: str) -> SimulationResult | None:
        result = self.collection.find_one({"id": result_id})

        if result:
            return self._to_domain(result)

        return None

    def save_result(self, result: SimulationResult) -> SimulationResult:
        self.collection.insert_one(self._to_collection(result))

    def update_result(self, result: SimulationResult) -> SimulationResult:
        self.collection.find_one_and_update(
            {"id": str(result.id)}, {"$set": self._to_collection(result)}
        )

    def delete_result(self, result_id: str) -> bool:
        self.collection.delete_one({"id": result_id})
