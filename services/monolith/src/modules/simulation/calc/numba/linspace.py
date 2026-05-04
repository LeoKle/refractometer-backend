import numpy as np
from numba import njit


@njit
def linspace_numba(start, stop, num):
    arr = np.zeros(num, dtype=np.float64)

    if num == 1:
        arr[0] = start
        return arr

    step = (stop - start) / (num - 1)

    for i in range(num):
        arr[i] = start + step * i

    return arr
