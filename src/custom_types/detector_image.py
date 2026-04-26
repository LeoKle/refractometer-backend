from typing import List, Tuple
from pydantic import BaseModel, Field
import numpy as np


class DetectorImage(BaseModel):
    values: List[List[float]] = Field(
        ..., description="A 2D matrix representing the detector image"
    )
    shape: Tuple[int, int] = Field((2560, 2440))

    @classmethod
    def fromNumpyArray(cls, array: np.ndarray) -> "DetectorImage":
        values = array.tolist()
        shape = array.shape
        return cls(values=values, shape=shape)
