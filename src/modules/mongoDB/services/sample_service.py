from typing import TYPE_CHECKING

from bson.objectid import ObjectId
from pymongo.database import Database

from custom_types.sample import Sample
from interfaces.database.services.sample_service_interface import ISampleService

if TYPE_CHECKING:
    from pymongo.collection import Collection


class SampleService(ISampleService):
    def __init__(self, db: Database, collection_name: str):
        self.collection: Collection = db[collection_name]

    def get_samples(self) -> list[Sample] | None:
        sample_data = self.collection.find({})

        samples = [
            Sample(
                name=sample["name"],
                id=str(sample["_id"]),
                sellmeier_coefficients=sample["sellmeierCoefficients"],
            )
            for sample in sample_data
        ]

        return samples or None

    def load_sample(self, sample_id: str) -> Sample | None:
        sample_data = self.collection.find_one({"_id": ObjectId(sample_id)})
        if sample_data:
            return Sample(
                name=sample_data["name"],
                id=str(sample_data["_id"]),
                sellmeier_coefficients=sample_data["sellmeierCoefficients"],
            )
        return None

    def save_sample(self, sample: Sample):
        self.collection.insert_one({
            "name": sample.name,
            "sellmeierCoefficients": sample.sellmeier_coefficients.model_dump(),
        })

    def update_sample(self, sample: Sample):
        if not sample.id:
            raise ValueError

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

    def delete_sample(self, sample_id: str):
        self.collection.delete_one({"_id": ObjectId(sample_id)})
