from pydantic import BaseModel
from custom_types.vector import Vector


class LightsourceParameters(BaseModel):
    direction_vector: Vector
    support_vector: Vector

    gap_height_meters: float
    count_rays_height: int
    gap_width_meters: float
    count_rays_width: int

    ray_divergence_degrees: float
    count_diverging_rays: int
