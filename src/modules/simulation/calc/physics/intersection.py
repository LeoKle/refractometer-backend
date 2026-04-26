from numba import njit

from backend.src.modules.simulation.calc.numba.vector import dot_product_vectors


@njit
def calculate_intersection_line_plane(
    plane_normal_vector,
    plane_support_vector,
    line_direction_vector,
    line_support_vector,
):
    nominator = dot_product_vectors(
        plane_normal_vector, plane_support_vector
    ) - dot_product_vectors(plane_normal_vector, line_support_vector)
    denomintor = dot_product_vectors(plane_normal_vector, line_direction_vector)

    if denomintor == 0:
        raise ValueError("The line is parallel to the plane or within the plane")

    t = nominator / denomintor

    intersection = line_support_vector + line_direction_vector * t

    return intersection
