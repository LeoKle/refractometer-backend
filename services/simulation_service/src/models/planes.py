from pydantic import BaseModel

from models.vector import Vector


class Plane(BaseModel):
    normal_vector: Vector
    support_vector: Vector


class PlaneGeometry(BaseModel):
    base_vector: Vector
    entry_angle: float
    prism_angle: float
    distance1: float
    distance2: float
