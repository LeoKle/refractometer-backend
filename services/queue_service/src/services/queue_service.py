from pymongo import ReturnDocument
from pymongo.collection import Collection

from interfaces.queue_service_interface import QueueServiceInterface
from models.queue_element import QueueElement

SAGA_FIELDS = {"attempts", "last_error"}


class QueueService(QueueServiceInterface):
    def __init__(self, collection: Collection, max_attempts: int = 3):
        self.collection = collection
        self.max_attempts = max_attempts

    @staticmethod
    def _to_domain(document: dict) -> QueueElement:
        return QueueElement(
            id=document["id"],
            issued_at=document["issued_at"],
            parameters=document["parameters"],
            issuer=document["issuer"],
            being_processed=document["being_processed"],
            callback_url=document["callback_url"],
            name=document.get("name"),
            attempts=document.get("attempts", 0),
            last_error=document.get("last_error"),
        )

    @staticmethod
    def _to_collection(queued_element: QueueElement) -> dict:
        return queued_element.model_dump(mode="json", exclude={"index"})

    def get_queued_simulations(self) -> list[QueueElement]:
        results = self.collection.find({}).sort("_id", 1)
        return [self._to_domain(result) for result in results]

    def load_queued_simulation(self, queue_id: str) -> QueueElement | None:
        result = self.collection.find_one({"id": queue_id})

        if result:
            return self._to_domain(result)

        return None

    def save_queued_simulation(self, queued_element: QueueElement) -> QueueElement:
        self.collection.insert_one(self._to_collection(queued_element))
        return queued_element

    def update_queued_simulation(self, queued_element: QueueElement):
        self.collection.find_one_and_update(
            {"id": str(queued_element.id)},
            {"$set": queued_element.model_dump(mode="json", exclude={"index", *SAGA_FIELDS})},
        )

    def delete_queued_simulation(self, queue_id: str):
        self.collection.delete_one({"id": queue_id})

    def claim_next_simulation(self) -> QueueElement | None:
        entry = self.collection.find_one_and_update(
            # $not/$gte to match documents that do not have a "attempts" field
            {"being_processed": False, "attempts": {"$not": {"$gte": self.max_attempts}}},
            # counting on claim (not on release) so crashed attempts count too
            {"$set": {"being_processed": True}, "$inc": {"attempts": 1}},
            sort=[("_id", 1)],
            return_document=ReturnDocument.AFTER,
        )

        if not entry:
            return None

        return self._to_domain(entry)

    def release_simulation(self, queue_id: str, error: str | None = None) -> bool:
        result = self.collection.update_one(
            {"id": queue_id},
            {"$set": {"being_processed": False, "last_error": error}},
        )
        return result.matched_count == 1

    def complete_simulation(self, queue_id: str) -> None:
        self.collection.delete_one({"id": queue_id})
