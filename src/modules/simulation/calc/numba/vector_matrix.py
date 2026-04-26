import numpy as np
from numba import njit


@njit
def dot_product_matrix_vector(matrix, vector):
    if matrix.shape[1] != vector.shape[0]:
        raise ValueError("Matrix and vector dimensions do not match.")

    result = np.zeros(matrix.shape[0])

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            result[i] += matrix[i, j] * vector[j]

    return result
