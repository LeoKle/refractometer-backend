from pymongo import ReturnDocument
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from interfaces.simulation_repository_interface import SimulationResultRepositoryInterface
from models.simulation_result import SimulationResult

IDEMPOTENCY_FIELD = "idempotency_key"


class SimulationResultRepository(SimulationResultRepositoryInterface):
    def __init__(self, collection: Collection):
        self.collection: Collection = collection
        # only documents saved with a key are indexed, saves without a key are not deduplicated
        self.collection.create_index(
            IDEMPOTENCY_FIELD,
            name="uniq_idempotency_key",
            unique=True,
            partialFilterExpression={IDEMPOTENCY_FIELD: {"$exists": True}},
        )

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
        result = self.collection.find_one({"id": str(result_id)})

        if result:
            return self._to_domain(result)

        return None

    def save_result(
        self, result: SimulationResult, idempotency_key: str | None = None
    ) -> SimulationResult:
        if idempotency_key is not None:
            existing = self._find_by_idempotency_key(idempotency_key)
            if existing is not None:
                return existing

        document = self._to_collection(result)
        if idempotency_key is not None:
            document[IDEMPOTENCY_FIELD] = idempotency_key

        try:
            self.collection.insert_one(document)
        except DuplicateKeyError:
            # a concurrent save with the same key won the race between find and insert
            existing = (
                self._find_by_idempotency_key(idempotency_key)
                if idempotency_key is not None
                else None
            )
            if existing is None:
                raise
            return existing

        return result

    def _find_by_idempotency_key(self, idempotency_key: str) -> SimulationResult | None:
        document = self.collection.find_one({IDEMPOTENCY_FIELD: idempotency_key})
        return self._to_domain(document) if document else None

    def update_result(self, result: SimulationResult) -> SimulationResult | None:
        doc = self.collection.find_one_and_update(
            {"id": str(result.id)},
            {"$set": self._to_collection(result)},
            return_document=ReturnDocument.AFTER,
        )

        if not doc:
            return None

        return self._to_domain(doc)

    def delete_result(self, result_id: str) -> bool:
        self.collection.delete_one({"id": result_id})
