"""Numba compiled Numpy vector functions"""

import numpy as np
from numba import njit

from modules.simulation.calc.numba.matrix import dot_product_matrix_matrix
from modules.simulation.calc.numba.vector_matrix import dot_product_matrix_vector


@njit
def normalize_vector(vector):
    """Returns the vector normalized (length == 1)"""

    return vector / length_vector(vector)


@njit
def length_vector(vector):
    squared_sum = 0.0
    for i in range(vector.size):
        squared_sum += vector[i] ** 2

    return np.sqrt(squared_sum)


@njit
def dot_product_vectors(vector1, vector2):
    if vector1.size != vector2.size:
        msg = "Vector sizes do not match"
        raise ValueError(msg)

    result = 0
    for i in range(vector1.size):
        result += vector1[i] * vector2[i]

    return result


@njit
def cross_product(vector1, vector2):
    if vector1.size != vector2.size:
        raise ValueError

    result = np.zeros(3, dtype=np.float64)
    result[0] = vector1[1] * vector2[2] - vector1[2] * vector2[1]
    result[1] = vector1[2] * vector2[0] - vector1[0] * vector2[2]
    result[2] = vector1[0] * vector2[1] - vector1[1] * vector2[0]
    return result


@njit
def rotate_vector_3d(vector, rotation_radians_x, rotation_radians_y, rotation_radians_z):
    """Rotates a 3D vector by the given radians with radians > 0 resulting in a counterclockwise rotation"""  # noqa: E501

    x_sin = np.sin(rotation_radians_x)
    x_cos = np.cos(rotation_radians_x)

    # specifying 0 and 1 as floats helps Numba with type assertion
    x_rotation_matrix = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, x_cos, -x_sin],
            [0.0, x_sin, x_cos],
        ],
        np.float64,
    )

    y_sin = np.sin(rotation_radians_y)
    y_cos = np.cos(rotation_radians_y)

    y_rotation_matrix = np.array([
        [y_cos, 0.0, y_sin],
        [0.0, 1.0, 0.0],
        [-y_sin, 0.0, y_cos],
    ])

    z_sin = np.sin(rotation_radians_z)
    z_cos = np.cos(rotation_radians_z)

    z_rotation_matrix = np.array([
        [z_cos, -z_sin, 0.0],
        [z_sin, z_cos, 0.0],
        [0.0, 0.0, 1.0],
    ])

    rotation_matrix = dot_product_matrix_matrix(x_rotation_matrix, y_rotation_matrix)
    rotation_matrix = dot_product_matrix_matrix(rotation_matrix, z_rotation_matrix)

    return normalize_vector(dot_product_matrix_vector(rotation_matrix, vector))
