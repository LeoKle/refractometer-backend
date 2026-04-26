import unittest
import numpy as np
from tests.modules.simulation.calc.numba import njit, prange
import math

from modules.simulation.calc.numba.vector import rotate_vector_3d

DEGREES = math.pi / 180


class TestVectorRotation(unittest.TestCase):
    def normalize_vector(self, vector):
        return vector / np.linalg.norm(vector)

    def test_rotate_vector(self):
        vector = np.array([1, 0, 0])
        radians_x = 0 * DEGREES
        radians_y = 0 * DEGREES
        radians_z = 90 * DEGREES

        np.testing.assert_allclose(
            rotate_vector_3d(vector, radians_x, radians_y, radians_z),
            np.array([0, 1, 0]),
            0.0001,
            0.0001,
        )

        vector = np.array([1, 0, 0])
        radians_x = 0 * DEGREES
        radians_y = 0 * DEGREES
        radians_z = 270 * DEGREES

        np.testing.assert_allclose(
            rotate_vector_3d(vector, radians_x, radians_y, radians_z),
            np.array([0, -1, 0]),
            0.0001,
            0.0001,
        )

    def test_rotate_vector_3d(self):
        # x - rotations
        vector = np.array([1, 1, 1])
        radians_x = -15 * DEGREES
        radians_y = 0 * DEGREES
        radians_z = 0 * DEGREES

        np.testing.assert_allclose(
            rotate_vector_3d(vector, radians_x, radians_y, radians_z),
            self.normalize_vector(np.array([1, 1.224744, 0.707106])),
            0.0001,
            0.0001,
        )

        vector = np.array([1, 1, 1])
        radians_x = 15 * DEGREES
        radians_y = 0 * DEGREES
        radians_z = 0 * DEGREES

        np.testing.assert_allclose(
            rotate_vector_3d(vector, radians_x, radians_y, radians_z),
            self.normalize_vector(np.array([1, 0.707106, 1.224744])),
            0.0001,
            0.0001,
        )

        # y - rotations
        vector = np.array([1, 1, 1])
        radians_x = 0 * DEGREES
        radians_y = -15 * DEGREES
        radians_z = 0 * DEGREES

        np.testing.assert_allclose(
            rotate_vector_3d(vector, radians_x, radians_y, radians_z),
            self.normalize_vector(np.array([0.707106, 1, 1.224744])),
            0.0001,
            0.0001,
        )

        vector = np.array([1, 1, 1])
        radians_x = 0 * DEGREES
        radians_y = 15 * DEGREES
        radians_z = 0 * DEGREES

        np.testing.assert_allclose(
            rotate_vector_3d(vector, radians_x, radians_y, radians_z),
            self.normalize_vector(np.array([1.224744, 1, 0.707106])),
            0.0001,
            0.0001,
        )

        # z - rotations
        vector = np.array([1, 1, 1])
        radians_x = 0 * DEGREES
        radians_y = 0 * DEGREES
        radians_z = -15 * DEGREES

        np.testing.assert_allclose(
            rotate_vector_3d(vector, radians_x, radians_y, radians_z),
            self.normalize_vector(np.array([1.224744, 0.707106, 1])),
            0.0001,
            0.0001,
        )

        vector = np.array([1, 1, 1])
        radians_x = 0 * DEGREES
        radians_y = 0 * DEGREES
        radians_z = 15 * DEGREES

        np.testing.assert_allclose(
            rotate_vector_3d(vector, radians_x, radians_y, radians_z),
            self.normalize_vector(np.array([0.707106, 1.224744, 1])),
            0.0001,
            0.0001,
        )

        # simultaneous rotations
        vector = np.array([1, 1, 1])
        radians_x = -15 * DEGREES
        radians_y = -15 * DEGREES
        radians_z = -15 * DEGREES

        np.testing.assert_allclose(
            rotate_vector_3d(vector, radians_x, radians_y, radians_z),
            self.normalize_vector(np.array([0.924193, 1.015055, 1.056186])),
            0.0001,
            0.0001,
        )

        vector = np.array([1, 1, 1])
        radians_x = 15 * DEGREES
        radians_y = 15 * DEGREES
        radians_z = 15 * DEGREES

        np.testing.assert_allclose(
            rotate_vector_3d(vector, radians_x, radians_y, radians_z),
            self.normalize_vector(np.array([0.941831, 0.980379, 1.073223])),
            0.0001,
            0.0001,
        )

    def test_dot_product_matrix_vector_njit(self):
        """Tests if the function is callable from numba njit compiled function"""

        vector = np.array([1, 1, 1])
        radians_x = 15 * DEGREES
        radians_y = 15 * DEGREES
        radians_z = 15 * DEGREES

        @njit
        def function_njit():
            result = rotate_vector_3d(vector, radians_x, radians_y, radians_z)

        @njit(parallel=True)
        def function_njit_parallel():
            for _ in prange(10):  # pylint: disable=not-an-iterable
                result = rotate_vector_3d(vector, radians_x, radians_y, radians_z)

        function_njit()
        function_njit_parallel()
