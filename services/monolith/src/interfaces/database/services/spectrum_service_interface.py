from abc import ABC, abstractmethod

from custom_types.spectrum import Spectrum


class ISpectrumService(ABC):
    @abstractmethod
    def get_spectrums(self) -> list[Spectrum]:
        """Returns all available spectrum"""
        pass

    @abstractmethod
    def load_spectrum(self, spectrum_name: str) -> Spectrum | None:
        pass

    @abstractmethod
    def save_spectrum(self, spectrum_name: str, wavelengths: list[float], intensities: list[float]):
        pass

    @abstractmethod
    def update_spectrum(
        self,
        spectrum_name: str,
        new_wavelengths: list[float],
        new_intensities: list[float],
    ):
        pass

    @abstractmethod
    def delete_spectrum(self, spectrum_name: str):
        pass
