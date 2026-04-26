from typing import List
from pymongo.database import Database
from pymongo.collection import Collection
from bson.objectid import ObjectId

from backend.src.custom_types.simulation_queue import SimulationQueueElement
from backend.src.interfaces.database.services.simulation_queue_service_interface import (
    ISimulationQueueService,
)


class SimulationQueueService(ISimulationQueueService):
    def __init__(self, db: Database, collection_name: str):
        self.collection: Collection = db[collection_name]

    def get_queued_simulations(self) -> List[SimulationQueueElement]:
        results = self.collection.find({})

        simulation_results = [
            SimulationQueueElement(
                id=str(result["_id"]),
                issued_at=result["issued_at"],
                completed_at=result["completed_at"],
                parameters=result["parameters"],
                index=result["index"],
                issuer=result["issuer"],
                being_processed=result["being_processed"],
                callback_url=result["callback_url"],
            )
            for result in results
        ]

        return simulation_results

    def load_queued_simulation(self, queue_id: str) -> SimulationQueueElement | None:
        result = self.collection.find_one({"_id": ObjectId(queue_id)})

        if result:
            return SimulationQueueElement(
                id=str(result["_id"]),
                issued_at=result["issued_at"],
                completed_at=result["completed_at"],
                parameters=result["parameters"],
                index=result["index"],
                issuer=result["issuer"],
                being_processed=result["being_processed"],
                callback_url=result["callback_url"],
            )

    def get_next_index(self) -> int:
        last_element = self.collection.find_one(sort=[("index", -1)])
        if last_element and "index" in last_element:
            return last_element["index"] + 1
        return 1

    def save_queued_simulation(self, queued_element: SimulationQueueElement):
        next_index = self.get_next_index()
        queued_element.index = next_index
        self.collection.insert_one(queued_element.model_dump(exclude={"id"}))

    def update_queued_simulation(self, queued_element: SimulationQueueElement):
        if not queued_element.id:
            raise ValueError

        self.collection.update_one(
            {"_id": ObjectId(queued_element.id)},
            {
                "$set": {
                    "parameters": queued_element.parameters.model_dump(),
                    "issued_at": queued_element.issued_at,
                    "completed_at": queued_element.completed_at,
                    "index": queued_element.index,
                    "being_processed": queued_element.being_processed,
                    "issuer": queued_element.issuer,
                    "callback_url": queued_element.callback_url,
                }
            },
        )

    def reduce_all_indices_by_one(self):
        self.collection.update_many(
            {},  # Select all documents
            {"$inc": {"index": -1}},  # Decrement the 'index' field by 1
        )

    def delete_queued_simulation(self, queue_id: str):
        self.collection.delete_one({"_id": ObjectId(queue_id)})
        # lower all indices by one
        self.reduce_all_indices_by_one()

    def find_next_simulation(self) -> SimulationQueueElement | None:
        entry = self.collection.find_one({})
        if not entry:
            return None
        return self.load_queued_simulation(entry["_id"])
