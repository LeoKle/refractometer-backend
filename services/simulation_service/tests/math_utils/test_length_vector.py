import unittest

import numpy as np
from numba import njit, prange

from math_utils.vector import length_vector


class TestNumbaLengthVector(unittest.TestCase):
    def case_length_vector(self, vector):
        np.testing.assert_equal(length_vector(vector), np.linalg.norm(vector))

    def test_length_vector_3d(self):
        # unit vectors
        self.case_length_vector(np.array([1, 0, 0]))
        self.case_length_vector(np.array([0, 1, 0]))
        self.case_length_vector(np.array([0, 0, 1]))

        # negative unit vectors
        self.case_length_vector(np.array([-1, 0, 0]))
        self.case_length_vector(np.array([0, -1, 0]))
        self.case_length_vector(np.array([0, 0, -1]))

        # random values
        self.case_length_vector(np.array([5, 10, -5]))
        self.case_length_vector(np.array([-5, 0, -5]))
        self.case_length_vector(np.array([-10, -10, -10]))

    def test_length_vector_2d(self):
        # unit vectors
        self.case_length_vector(np.array([1, 0]))
        self.case_length_vector(np.array([0, 1]))

        # negative unit vectors
        self.case_length_vector(np.array([-1, 0]))
        self.case_length_vector(np.array([0, -1]))

        # random values
        self.case_length_vector(np.array([5, 10]))
        self.case_length_vector(np.array([-5, 0]))
        self.case_length_vector(np.array([-10, -10]))

    def test_length_vector_njit(self):
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
                length_vector(vector)

        @njit(parallel=True)
        def function_njit_parallel():
            for i in prange(vectors.shape[0]):
                length_vector(vectors[i])

        function_njit()
        function_njit_parallel()
