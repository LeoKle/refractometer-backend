from typing import List
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.results import DeleteResult
from backend.src.custom_types.spectrum import Spectrum
from backend.src.interfaces.database.services.spectrum_service_interface import (
    ISpectrumService,
)


class SpectrumService(ISpectrumService):
    def __init__(self, db: Database, collection_name: str):
        self.collection: Collection = db[collection_name]

    def get_spectrums(self) -> List[Spectrum]:
        spectra_data = self.collection.find({})

        spectra = []
        for spectrum_data in spectra_data:
            spectrum = Spectrum(
                name=spectrum_data["name"],
                id=str(spectrum_data["_id"]),
                wavelengths=spectrum_data["wavelengths"],
                intensities=spectrum_data["intensities"],
            )
            spectra.append(spectrum)
        return spectra

    def load_spectrum(self, spectrum_name) -> Spectrum | None:
        spectrum_data = self.collection.find_one({"name": spectrum_name})
        if spectrum_data is None:
            return None

        return Spectrum(
            name=spectrum_data["name"],
            id=str(spectrum_data["_id"]),
            wavelengths=spectrum_data["wavelengths"],
            intensities=spectrum_data["intensities"],
        )

    def save_spectrum(self, spectrum_name, wavelengths, intensities):
        self.collection.insert_one(
            {
                "name": spectrum_name,
                "wavelengths": wavelengths,
                "intensities": intensities,
            }
        )

    def update_spectrum(self, spectrum_name, new_wavelengths, new_intensities):
        self.collection.update_one(
            {"name": spectrum_name},
            {"$set": {"wavelengths": new_wavelengths, "intensities": new_intensities}},
            upsert=True,
        )

    def delete_spectrum(self, spectrum_name) -> bool:
        result: DeleteResult = self.collection.delete_one({"name": spectrum_name})
        if result.deleted_count > 0:
            return True  # Spectrum was deleted
        else:
            return False  # Spectrum was not found or not deleted
