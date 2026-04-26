from typing import List
from pymongo.database import Database
from pymongo.collection import Collection
from bson.objectid import ObjectId

from backend.src.custom_types.simulation_result import SimulationResult
from backend.src.interfaces.database.services.simulation_result_service_interface import (
    ISimulationResultService,
)


class SimulationResultService(ISimulationResultService):
    def __init__(self, db: Database, collection_name: str):
        self.collection: Collection = db[collection_name]

    def get_results(self) -> List[SimulationResult]:
        results = self.collection.find({})

        simulation_results = [
            SimulationResult(
                id=str(result["_id"]),
                issued_at=result["issued_at"],
                completed_at=result["completed_at"],
                parameters=result["parameters"],
                image_id=result["image_id"],
            )
            for result in results
        ]

        return simulation_results

    def load_result(self, result_id: str) -> SimulationResult | None:
        result = self.collection.find_one({"_id": ObjectId(result_id)})

        if not result:
            return

        return SimulationResult(
            id=str(result["_id"]),
            issued_at=result["issued_at"],
            completed_at=result["completed_at"],
            parameters=result["parameters"],
            image_id=result["image_id"],
        )

    def save_result(self, result: SimulationResult):
        self.collection.insert_one(result.model_dump(exclude="id"))

    def update_result(self, result: SimulationResult):
        if not result.id:
            raise ValueError

        self.collection.update_one(
            {"_id": ObjectId(result.id)},
            {
                "$set": {
                    "parameters": result.parameters.model_dump(),
                    "image": result.image.model_dump(),
                    "issued_at": result.issued_at,
                    "completed_at": result.completed_at,
                }
            },
        )

    def delete_result(self, result_id: str):
        self.collection.delete_one({"_id": ObjectId(result_id)})
