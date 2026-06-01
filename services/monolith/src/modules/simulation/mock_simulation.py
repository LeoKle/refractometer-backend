import time

import numpy as np

from custom_types.detector_image import DetectorImage
from custom_types.simulation_parameters import SimulationParameters
from custom_types.simulation_state import SimulationState, SimulationStates
from interfaces.app.simulation_interface import ISimulation


class MockSimulation(ISimulation):
    def __init__(self):
        self._parameters: SimulationParameters | None = None
        self._state = SimulationStates.IDLE.value
        self._image: DetectorImage | None = None

    def get_state(self) -> SimulationState:
        return self._state

    def set_parameters(self, simulation_params: SimulationParameters):
        self._parameters = simulation_params
        self._state = SimulationStates.SET_UP.value

    def simulate(self):
        self._state = SimulationStates.SIMULATING.value

        time.sleep(2)  # simulate work

        # create a mock detector image
        mock_array = np.random.random((256, 256))

        self._image = DetectorImage.fromNumpyArray(mock_array)
        self._state = SimulationStates.SIMULATION_DONE.value

    def get_detector_image(self) -> DetectorImage:
        if self._image is None:
            msg = "Simulation has not been run yet"
            raise RuntimeError(msg)

        return self._image
