import uuid

from pymongo.collection import Collection

from interfaces.repositories.spectrum_repository_interface import SpectrumRepositoryInterface
from models.spectrum import Spectrum


class SpectrumRepository(SpectrumRepositoryInterface):
    def __init__(self, collection: Collection):
        self.collection = collection

    def _doc_to_domain(self, doc: dict):
        return Spectrum(
            id=uuid.UUID(doc.get("id")),
            name=doc.get("name"),
            wavelengths=doc.get("wavelengths"),
            intensities=doc.get("intensities"),
        )

    def _domain_to_doc(self, model: Spectrum):
        return {
            "id": str(model.id),
            "name": model.name,
            "wavelengths": model.wavelengths,
            "intensities": model.intensities,
        }

    def find_all(self) -> list[Spectrum]:
        cursor = self.collection.find({})
        return [self._doc_to_domain(doc) for doc in cursor]

    def find_by_id(self, spectrum_id: uuid.UUID) -> Spectrum | None:
        doc = self.collection.find_one({"id": str(spectrum_id)})

        if doc is None:
            return None
        return self._doc_to_domain(doc)

    def insert(self, spectrum: Spectrum):
        doc = self._domain_to_doc(spectrum)
        self.collection.insert_one(doc)
        return spectrum

    def update(self, spectrum: Spectrum):
        self.collection.update_one(
            {"id": str(spectrum.id)},
            {"$set": self._domain_to_doc(spectrum)},
        )

        return spectrum

    def delete(self, spectrum_id: uuid.UUID) -> bool:
        result = self.collection.delete_one({"id": str(spectrum_id)})
        return result.deleted_count == 1
