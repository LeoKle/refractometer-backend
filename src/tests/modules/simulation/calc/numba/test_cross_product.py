import unittest
import numpy as np
from numba import njit, prange

from modules.simulation.calc.numba.vector import cross_product


class TestNumbaCrossProduct(unittest.TestCase):
    def case_cross_product(self, vector1, vector2):
        np.testing.assert_equal(
            cross_product(vector1, vector2), np.cross(vector1, vector2)
        )

    def test_dot_product_vectors_3d(self):
        self.case_cross_product(np.array([1, 0, 0]), np.array([0, 1, 0]))
        self.case_cross_product(np.array([1, 0, 0]), np.array([0, 0, 1]))

        self.case_cross_product(np.array([0, 1, 0]), np.array([1, 0, 0]))
        self.case_cross_product(np.array([0, 1, 0]), np.array([0, 0, 1]))

        self.case_cross_product(np.array([0, 0, 1]), np.array([1, 0, 0]))
        self.case_cross_product(np.array([0, 0, 1]), np.array([0, 1, 0]))

    def test_cross_product_invalid(self):
        with np.testing.assert_raises(ValueError):
            cross_product(np.array([1, 1, 1, 1]), np.array([0, 0, 0]))

        with np.testing.assert_raises(ValueError):
            cross_product(np.array([1, 1, 1]), np.array([0, 0, 0, 0]))

    def test_cross_product_njit(self):
        """Tests if the function is callable from numba njit compiled function"""
        vectors = np.array(
            [
                [1, 1, 1],
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
                [-5, -5, -5],
                [0, 0, 1],
                [0, 0, 1],
            ]
        )

        @njit
        def function_njit():
            for vector in vectors:
                cross_product(vector, vector)

        @njit(parallel=True)
        def function_njit_parallel():
            for i in prange(vectors.shape[0]):  # pylint: disable=not-an-iterable
                cross_product(vectors[i], vectors[i])

        function_njit()
        function_njit_parallel()
