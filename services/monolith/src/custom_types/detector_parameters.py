from pydantic import BaseModel, Field

from custom_types.detector_calibration import WavelengthCalibration
from custom_types.vector import Vector


class DetectorParameters(BaseModel):
    support_vector: Vector | None = Field(default=None)
    distance3: float
    normal_vector: Vector | WavelengthCalibration
    height_pixels: int
    width_pixels: int
    pixel_size_meters_per_pixel: float
