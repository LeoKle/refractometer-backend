from typing import List
import numpy as np
from numba import njit, prange

from backend.src.custom_types.lightsource_parameters import LightsourceParameters
from backend.src.custom_types.plane import Plane
from backend.src.custom_types.spectrum import Spectrum
from backend.src.modules.simulation.calc.numba.vector import rotate_vector_3d
from backend.src.modules.simulation.constants.units import DEGREES
from backend.src.modules.simulation.core.alloc_lightrays import alloc_arrays
from backend.src.modules.simulation.calc.numba.linspace import linspace_numba


def setup_lightrays(
    spectrum: Spectrum, lightsource: LightsourceParameters, planes: List[Plane]
):
    lightray_count = (
        len(spectrum.wavelengths)
        * lightsource.count_rays_height
        * lightsource.count_rays_width
        * lightsource.count_diverging_rays
    )

    plane_count = len(planes)

    direction_vectors, support_vectors, wavelengths, intensities = alloc_arrays(
        lightray_count, plane_count
    )

    # the angles to rotate the vector on
    if lightsource.count_diverging_rays == 1:
        angles = [0]
    else:
        angles = linspace_numba(
            -lightsource.ray_divergence_degrees / 2,
            lightsource.ray_divergence_degrees,
            lightsource.count_diverging_rays,
        )

    # the height shifts
    if lightsource.count_rays_height == 1:
        shifts_height = [0]
    else:
        shifts_height = linspace_numba(
            -lightsource.gap_height_meters / 2,
            lightsource.gap_height_meters / 2,
            lightsource.count_rays_height,
        )

    # the shift in position to apply to the lightrays
    if lightsource.count_rays_width == 1:
        shifts_width = [0]
    else:
        shifts_width = linspace_numba(
            -lightsource.gap_width_meters / 2,
            lightsource.gap_width_meters / 2,
            lightsource.count_rays_width,
        )

    # Loop over angles, shifts wavelengths and intensities to create combinations
    combinations = []
    for angle in angles:
        for height_shift in shifts_height:
            for width_shift in shifts_width:
                for wavelength, intensity in zip(
                    spectrum.wavelengths, spectrum.intensities
                ):
                    combinations.append(
                        (
                            angle * DEGREES,
                            height_shift,
                            width_shift,
                            wavelength,
                            intensity,
                        )
                    )

    return test(
        np.array(lightsource.direction_vector.to_list()),
        np.array(lightsource.support_vector.to_list()),
        direction_vectors,
        support_vectors,
        wavelengths,
        intensities,
        combinations,
    )


@njit(parallel=True)
def test(
    lightsource_direction_vector,
    lightsource_support_vector,
    direction_vectors,
    support_vectors,
    wavelengths,
    intensities,
    combinations,
):
    for i in prange(direction_vectors.shape[0]):
        direction_vectors[i, 0] = rotate_vector_3d(
            lightsource_direction_vector, 0, 0, combinations[i][0]
        )

        # apply the height and width shift
        support_vectors[i, 0] = lightsource_support_vector + np.array(
            [0, combinations[i][2], combinations[i][1]]
        )

        wavelengths[i] = combinations[i][3]
        intensities[i, 0] = combinations[i][4]

    return direction_vectors, support_vectors, wavelengths, intensities
