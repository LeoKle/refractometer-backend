import uuid
from abc import ABC, abstractmethod

from models.spectrum import Spectrum


class SpectrumServiceInterface(ABC):
    @abstractmethod
    def get_spectrums(self) -> list[Spectrum]: ...

    @abstractmethod
    def get_spectrum(self, id: uuid.UUID) -> Spectrum | None: ...

    @abstractmethod
    def save_spectrum(self, spectrum: Spectrum) -> Spectrum: ...

    @abstractmethod
    def update_spectrum(self, spectrum: Spectrum) -> Spectrum: ...

    @abstractmethod
    def delete_spectrum(self, id: uuid.UUID) -> bool: ...
