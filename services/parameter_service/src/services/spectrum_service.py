import uuid

from interfaces.repositories.spectrum_repository_interface import (
    SpectrumRepositoryInterface,
)
from interfaces.services.spectrum_service_interface import SpectrumServiceInterface
from models.spectrum import Spectrum


class SpectrumService(SpectrumServiceInterface):
    def __init__(self, repository: SpectrumRepositoryInterface):
        self.repo = repository

    def get_spectrums(self) -> list[Spectrum]:
        return self.repo.find_all()

    def get_spectrum(self, id: uuid.UUID) -> Spectrum | None:
        return self.repo.find_by_id(id)

    def save_spectrum(self, spectrum: Spectrum) -> Spectrum:
        return self.repo.insert(spectrum)

    def update_spectrum(self, spectrum: Spectrum) -> Spectrum:
        existing = self.repo.find_by_id(spectrum.id)

        if existing is None:
            msg = f"Spectrum with id {spectrum.id} not found"
            raise ValueError(msg)

        return self.repo.update(spectrum)

    def delete_spectrum(self, id: uuid.UUID) -> bool:
        return self.repo.delete(id)
