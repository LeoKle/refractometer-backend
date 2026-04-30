from abc import ABC, abstractmethod
from typing import List

from custom_types.spectrum import Spectrum


class ISpectrumService(ABC):
    @abstractmethod
    def get_spectrums(self) -> List[Spectrum]:
        """Returns all available spectrum"""
        pass

    @abstractmethod
    def load_spectrum(self, spectrum_name: str) -> Spectrum | None:
        pass

    @abstractmethod
    def save_spectrum(self, spectrum_name: str, wavelengths: List[float], intensities: List[float]):
        pass

    @abstractmethod
    def update_spectrum(
        self,
        spectrum_name: str,
        new_wavelengths: List[float],
        new_intensities: List[float],
    ):
        pass

    @abstractmethod
    def delete_spectrum(self, spectrum_name: str):
        pass
