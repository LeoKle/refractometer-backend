from pydantic import BaseModel, Field

from models.vector import Vector


class WavelengthCalibration(BaseModel):
    """
    Alternate way to define the normal vector of the detector
    We are calibrating the detector to have
    """

    wavelength: float


class DetectorParameters(BaseModel):
    support_vector: Vector | None = Field(default=None)
    distance3: float
    normal_vector: Vector | WavelengthCalibration
    height_pixels: int
    width_pixels: int
    pixel_size_meters_per_pixel: float
