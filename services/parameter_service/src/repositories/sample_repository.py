from bson.objectid import ObjectId
from pymongo.collection import Collection

from interfaces.repositories.sample_repository_interface import ISampleRepository
from models.sample import Sample


class SampleRepository(ISampleRepository):
    def __init__(self, collection: Collection):
        self.collection: Collection = collection

    def find_all(self) -> list[Sample]:
        return [
            Sample(
                name=sample["name"],
                id=str(sample["_id"]),
                sellmeier_coefficients=sample["sellmeierCoefficients"],
            )
            for sample in self.collection.find({})
        ]

    def find_by_id(self, sample_id: str) -> Sample | None:
        sample_data = self.collection.find_one({"_id": ObjectId(sample_id)})
        if sample_data:
            return Sample(
                name=sample_data["name"],
                id=str(sample_data["_id"]),
                sellmeier_coefficients=sample_data["sellmeierCoefficients"],
            )
        return None

    def insert(self, sample: Sample):
        self.collection.insert_one({
            "name": sample.name,
            "sellmeierCoefficients": sample.sellmeier_coefficients.model_dump(),
        })

    def update(self, sample: Sample):
        if not sample.id:
            msg = "Sample must have an id to be updated"
            raise ValueError(msg)

        self.collection.update_one(
            {"_id": ObjectId(sample.id)},
            {
                "$set": {
                    "name": sample.name,
                    "sellmeierCoefficients": sample.sellmeier_coefficients.model_dump(),
                }
            },
            upsert=True,
        )

    def delete(self, sample_id: str):
        self.collection.delete_one({"_id": ObjectId(sample_id)})
