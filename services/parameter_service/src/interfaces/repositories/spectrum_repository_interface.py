from abc import ABC, abstractmethod

from models.spectrum import Spectrum


class SpectrumRepositoryInterface(ABC):
    @abstractmethod
    def find_all(self) -> list[Spectrum]: ...

    @abstractmethod
    def find_by_id(self, spectrum_id: str) -> Spectrum | None: ...

    @abstractmethod
    def insert(self, spectrum: Spectrum): ...

    @abstractmethod
    def update(self, spectrum: Spectrum): ...

    @abstractmethod
    def delete(self, spectrum_id: str): ...
