import unittest
import numpy as np
from tests.modules.simulation.calc.numba import njit, prange

from modules.simulation.calc.numba.vector import normalize_vector


class TestNumbaNormalizeVector(unittest.TestCase):
    def case_normalize_vector(self, vector):
        np.testing.assert_equal(
            normalize_vector(vector), vector / np.linalg.norm(vector)
        )

    def test_length_vector_3d(self):
        # unit vectors
        self.case_normalize_vector(np.array([1, 0, 0]))
        self.case_normalize_vector(np.array([0, 1, 0]))
        self.case_normalize_vector(np.array([0, 0, 1]))

        # negative unit vectors
        self.case_normalize_vector(np.array([-1, 0, 0]))
        self.case_normalize_vector(np.array([0, -1, 0]))
        self.case_normalize_vector(np.array([0, 0, -1]))

        # random values
        self.case_normalize_vector(np.array([5, 10, -5]))
        self.case_normalize_vector(np.array([-5, 0, -5]))
        self.case_normalize_vector(np.array([-10, -10, -10]))

    def test_length_vector_2d(self):
        # unit vectors
        self.case_normalize_vector(np.array([1, 0]))
        self.case_normalize_vector(np.array([0, 1]))

        # negative unit vectors
        self.case_normalize_vector(np.array([-1, 0]))
        self.case_normalize_vector(np.array([0, -1]))

        # random values
        self.case_normalize_vector(np.array([5, 10]))
        self.case_normalize_vector(np.array([-5, 0]))
        self.case_normalize_vector(np.array([-10, -10]))

    def test_normalize_vector_njit(self):
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
                normalize_vector(vector)

        @njit(parallel=True)
        def function_njit_parallel():
            for i in prange(vectors.shape[0]):  # pylint: disable=not-an-iterable
                normalize_vector(vectors[i])

        function_njit()
        function_njit_parallel()
