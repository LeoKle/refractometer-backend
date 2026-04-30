from pydantic import BaseModel

from custom_types.detector_parameters import DetectorParameters
from custom_types.lightsource_parameters import LightsourceParameters
from custom_types.plane import Plane, PlaneGeometry
from custom_types.sample import Sample
from custom_types.spectrum import Spectrum


class SimulationParameters(BaseModel):
    lightsource: LightsourceParameters
    spectrum: Spectrum
    sample: Sample
    planes: PlaneGeometry | list[Plane]
    detector: DetectorParameters
