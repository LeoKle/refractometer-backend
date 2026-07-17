import numpy as np
from pydantic import BaseModel, Field


class DetectorImage(BaseModel):
    values: list[list[float]] = Field(
        ..., description="A 2D matrix representing the detector image"
    )
    shape: tuple[int, int] = Field((2560, 2440))

    @classmethod
    def fromNumpyArray(cls, array: np.ndarray) -> "DetectorImage":
        array = np.nan_to_num(array, nan=0.0)
        values = array.tolist()
        shape = array.shape
        return cls(values=values, shape=shape)
