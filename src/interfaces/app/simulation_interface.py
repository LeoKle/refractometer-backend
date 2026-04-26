from abc import ABC, abstractmethod

from backend.src.custom_types.simulation_parameters import SimulationParameters
from backend.src.custom_types.detector_image import DetectorImage
from backend.src.custom_types.simulation_state import SimulationState


class ISimulation(ABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ISimulation, cls).__new__(cls)
        return cls._instance

    @abstractmethod
    def get_state(self) -> SimulationState:
        pass

    @abstractmethod
    def set_parameters(self, simulation_params=SimulationParameters):
        """Sets all parameters the simulation uses"""
        pass

    @abstractmethod
    def simulate(self):
        """Simulates each lightray until they exit the sample"""
        pass

    @abstractmethod
    def get_detector_image(self) -> DetectorImage:
        pass
