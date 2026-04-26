from typing import List
from pydantic import BaseModel

from backend.src.custom_types.detector_parameters import DetectorParameters
from backend.src.custom_types.plane import Plane, PlaneGeometry
from backend.src.custom_types.sample import Sample
from backend.src.custom_types.spectrum import Spectrum
from backend.src.custom_types.lightsource_parameters import LightsourceParameters


class SimulationParameters(BaseModel):
    lightsource: LightsourceParameters
    spectrum: Spectrum
    sample: Sample
    planes: PlaneGeometry | List[Plane]
    detector: DetectorParameters
