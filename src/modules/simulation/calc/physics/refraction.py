import math
from numba import njit

from modules.simulation.calc.numba.vector import dot_product_vectors, normalize_vector


@njit
def refracted_direction_vector(
    refractive_index_1, refractive_index_2, direction_vector_light, normal_vector_plane
):
    direction_vector_light = normalize_vector(direction_vector_light)
    normal_vector_plane = normalize_vector(normal_vector_plane)

    if refractive_index_1 <= 0 or refractive_index_2 <= 0:
        raise ValueError("refractive indices must be > 0")

    refractive_index_ratio = refractive_index_1 / refractive_index_2

    first_term = refractive_index_ratio * direction_vector_light

    second_term = normal_vector_plane * (
        refractive_index_ratio
        * (dot_product_vectors(normal_vector_plane, direction_vector_light))
        - math.sqrt(
            1
            - math.pow(refractive_index_ratio, 2)
            * (
                1
                - math.pow(
                    dot_product_vectors(normal_vector_plane, direction_vector_light), 2
                )
            )
        )
    )

    new_direction_vector = first_term - second_term

    return new_direction_vector
