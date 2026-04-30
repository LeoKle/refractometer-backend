import numpy as np
from numba import njit


@njit
def alloc_arrays(lightray_count: int, plane_count: int):
    # we need to allocate one additional section for the initial values
    sections = plane_count + 1

    direction_vectors = np.zeros((lightray_count, sections, 3), dtype=np.float64)
    support_vectors = np.zeros((lightray_count, sections, 3), dtype=np.float64)
    wavelengths = np.zeros(lightray_count, dtype=np.float64)
    intensities = np.zeros((lightray_count, sections), dtype=np.float64)

    return direction_vectors, support_vectors, wavelengths, intensities
