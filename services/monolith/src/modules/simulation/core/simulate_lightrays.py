from numba import njit, prange

from modules.simulation.calc.physics.intersection import (
    calculate_intersection_line_plane,
)
from modules.simulation.calc.physics.refraction import refracted_direction_vector


@njit(parallel=True, nogil=True)
def simulate_lightrays(
    direction_vectors,
    support_vectors,
    wavelengths,
    intensities,
    plane_normal_vectors,
    plane_support_vectors,
    refractive_indices,
):
    refractive_index_air = 1.000293

    for lightray in prange(direction_vectors.shape[0]):
        refractive_index = refractive_indices[lightray]

        for plane in range(plane_normal_vectors.shape[0]):
            intersection = calculate_intersection_line_plane(
                plane_normal_vectors[plane],
                plane_support_vectors[plane],
                direction_vectors[lightray, plane],
                support_vectors[lightray, plane],
            )

            direction_vectors[lightray, plane + 1] = refracted_direction_vector(
                refractive_index_air if plane == 0 else refractive_index,
                refractive_index if plane == 0 else refractive_index_air,
                direction_vectors[lightray, plane],
                plane_normal_vectors[plane],
            )

            support_vectors[lightray, plane + 1] = intersection

            intensities[lightray, plane + 1] = intensities[lightray, plane]

    return direction_vectors, support_vectors, wavelengths, intensities
