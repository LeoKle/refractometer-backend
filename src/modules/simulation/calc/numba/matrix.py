import numpy as np
from numba import njit, prange


@njit(parallel=True)
def dot_product_matrix_matrix(matrix1, matrix2):
    if matrix1.shape[1] != matrix2.shape[0]:
        msg = "Matrix dimensions do not allow multiplication."
        raise ValueError(msg)

    result = np.zeros((matrix1.shape[0], matrix2.shape[1]))

    for i in prange(matrix1.shape[0]):  # pylint: disable=not-an-iterable
        for j in prange(matrix2.shape[1]):  # pylint: disable=not-an-iterable
            for k in prange(matrix1.shape[1]):  # pylint: disable=not-an-iterable
                result[i, j] += matrix1[i, k] * matrix2[k, j]

    return result
