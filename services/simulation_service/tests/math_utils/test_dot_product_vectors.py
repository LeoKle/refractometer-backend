import unittest

import numpy as np
from numba import njit, prange

from math_utils.vector import dot_product_vectors


class TestNumbaDotProductVectors(unittest.TestCase):
    def case_dot_product_vectors(self, vector1, vector2):
        np.testing.assert_equal(dot_product_vectors(vector1, vector2), np.dot(vector1, vector2))

    def test_dot_product_vectors_3d(self):
        self.case_dot_product_vectors(np.array([1, 0, 0]), np.array([2, 0, 0]))
        self.case_dot_product_vectors(np.array([2, 0, 0]), np.array([4, 0, 0]))
        self.case_dot_product_vectors(np.array([-2, 0, 0]), np.array([-2, 0, 0]))

        self.case_dot_product_vectors(np.array([-2, -2, -2]), np.array([-2, -2, -2]))
        self.case_dot_product_vectors(np.array([-2, 5, 5]), np.array([-2, 0, 0]))
        self.case_dot_product_vectors(np.array([-2, -5, -5]), np.array([2, 10, 100]))

        self.case_dot_product_vectors(np.array([1, 2, 3]), np.array([4, 5, 6]))
        self.case_dot_product_vectors(np.array([-1, -2, -3]), np.array([-4, -5, -6]))

        # zero scalar result
        self.case_dot_product_vectors(np.array([1, 0, 0]), np.array([0, 1, 0]))
        self.case_dot_product_vectors(np.array([0, 0, 1]), np.array([0, 0, 0]))

    def test_dot_product_vectors_2d(self):
        self.case_dot_product_vectors(np.array([1, 0]), np.array([2, 0]))
        self.case_dot_product_vectors(np.array([2, 0]), np.array([4, 0]))
        self.case_dot_product_vectors(np.array([-2, 0]), np.array([-2, 0]))

        self.case_dot_product_vectors(np.array([-2, -2]), np.array([-2, -2]))
        self.case_dot_product_vectors(np.array([-2, 5]), np.array([-2, 0]))
        self.case_dot_product_vectors(np.array([-2, -5]), np.array([2, 10]))

        self.case_dot_product_vectors(np.array([1, 2]), np.array([4, 5]))
        self.case_dot_product_vectors(np.array([-1, -2]), np.array([-4, -5]))

        # zero scalar result
        self.case_dot_product_vectors(np.array([1, 0]), np.array([0, 1]))
        self.case_dot_product_vectors(np.array([0, 0]), np.array([0, 0]))

    def test_dot_product_vectors_1d(self):
        self.case_dot_product_vectors(np.array([1]), np.array([2]))
        self.case_dot_product_vectors(np.array([-1]), np.array([-2]))

    def test_dot_product_vectors_invalid_inputs(self):
        with self.assertRaises(ValueError):
            self.case_dot_product_vectors(np.array([1, 2, 3]), np.array([4, 5]))

    def test_dot_product_vectors_large_values(self):
        self.case_dot_product_vectors(np.array([10**9, 10**9, 10**9]), np.array([1, 0, 0]))
        self.case_dot_product_vectors(np.array([-(10**9), -(10**9), -(10**9)]), np.array([1, 1, 1]))

    def test_dot_product_vectors_zero_vectors(self):
        self.case_dot_product_vectors(np.array([0, 0, 0]), np.array([1, 2, 3]))
        self.case_dot_product_vectors(np.array([1, 2, 3]), np.array([0, 0, 0]))
        self.case_dot_product_vectors(np.array([0, 0, 0]), np.array([0, 0, 0]))

    def test_dot_product_vectors_njit(self):
        """Tests if the function is callable from numba njit compiled function"""
        vectors = np.array([
            [1, 1, 1],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [-5, -5, -5],
            [0, 0, 1],
            [0, 0, 1],
        ])

        @njit
        def function_njit():
            for vector in vectors:
                dot_product_vectors(vector, vector)

        @njit(parallel=True)
        def function_njit_parallel():
            for i in prange(vectors.shape[0]):
                dot_product_vectors(vectors[i], vectors[i])

        function_njit()
        function_njit_parallel()
