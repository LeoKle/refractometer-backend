import numpy as np
from typing import List
from pydantic import BaseModel


class Vector(BaseModel):
    x: float
    y: float
    z: float

    @classmethod
    def from_list(cls, values: List[float]):
        if len(values) != 3:
            raise ValueError("List must contain exactly three elements")
        return cls(x=values[0], y=values[1], z=values[2])

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]

    def to_numpy_array(self) -> np.ndarray:
        return np.array(self.to_list())


class VectorByDistance(BaseModel):
    base_vector: Vector
    x_distance: float
    y_distance: float
    z_distance: float


class VectorByRotation(BaseModel):
    base_vector: Vector
    x_rotation_degrees: float
    y_rotation_degrees: float
    z_rotation_degrees: float
