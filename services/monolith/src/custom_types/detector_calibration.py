from pydantic import BaseModel


class WavelengthCalibration(BaseModel):
    """
    Alternate way to define the normal vector of the detector
    We are calibrating the detector to have
    """

    wavelength: float
