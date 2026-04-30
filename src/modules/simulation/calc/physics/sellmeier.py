import math

from numba import njit


@njit
def sellmeier_equation(b, c, wavelength_meters):
    # convert wavelength in meters to wavelength in micrometers
    wavelength_squared = (wavelength_meters * 1e6) ** 2

    term_sum = 0.0
    for n in range(len(b)):
        term_sum += (b[n] * wavelength_squared) / (wavelength_squared - c[n])

    n_squared = 1 + term_sum
    return math.sqrt(n_squared)
