from constants import DEGREES
from math_utils.vector import rotate_vector_3d
from models.planes import Plane, PlaneGeometry
from models.vector import Vector


def setup_planes(plane_params=PlaneGeometry) -> list[Plane]:
    # create the first normal vector by rotation
    normal_vector1 = rotate_vector_3d(
        plane_params.base_vector.to_numpy_array(),
        rotation_radians_x=0,
        rotation_radians_y=0,
        rotation_radians_z=-plane_params.entry_angle * DEGREES,
    )
    # create the second normal vector using the known prism angle
    normal_vector2 = rotate_vector_3d(
        normal_vector1,
        rotation_radians_x=0,
        rotation_radians_y=0,
        rotation_radians_z=plane_params.prism_angle * DEGREES,
    )

    support_vector1 = plane_params.base_vector.to_numpy_array() * plane_params.distance1
    support_vector2 = plane_params.base_vector.to_numpy_array() * plane_params.distance2

    planes = []
    planes.extend((
        Plane(
            normal_vector=Vector.from_list(normal_vector1),
            support_vector=Vector.from_list(support_vector1),
        ),
        Plane(
            normal_vector=Vector.from_list(normal_vector2),
            support_vector=Vector.from_list(support_vector2),
        ),
    ))

    return planes
