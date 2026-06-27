import uuid

from pymongo.collection import Collection

from interfaces.repositories.sample_repository_interface import ISampleRepository
from models.sample import Sample


class SampleRepository(ISampleRepository):
    def __init__(self, collection: Collection):
        self.collection: Collection = collection
        collection.create_index("id", unique=True)

    def find_all(self) -> list[Sample]:
        return [
            Sample(
                name=sample.get("name"),
                id=str(sample.get("id")),
                sellmeier_coefficients=sample.get("sellmeierCoefficients"),
            )
            for sample in self.collection.find({})
            if "name" in sample and "sellmeierCoefficients" in sample
        ]

    def find_by_id(self, sample_id: str) -> Sample | None:
        sample_data = self.collection.find_one({"id": sample_id})

        if not sample_data:
            return None

        return Sample(
            name=sample_data.get("name"),
            id=uuid.UUID(sample_data.get("id")),
            sellmeier_coefficients=sample_data.get("sellmeierCoefficients"),
        )

    def insert(self, sample: Sample):
        self.collection.insert_one({
            "id": str(sample.id),
            "name": sample.name,
            "sellmeierCoefficients": sample.sellmeier_coefficients.model_dump(),
        })

    def update(self, sample: Sample):
        result = self.collection.update_one(
            {"id": str(sample.id)},
            {
                "$set": {
                    "name": sample.name,
                    "sellmeierCoefficients": sample.sellmeier_coefficients.model_dump(),
                }
            },
        )
        if result.matched_count == 0:
            msg = f"Sample with id {sample.id} not found"
            raise KeyError(msg)

    def delete(self, sample_id: str):
        self.collection.delete_one({"id": sample_id})
