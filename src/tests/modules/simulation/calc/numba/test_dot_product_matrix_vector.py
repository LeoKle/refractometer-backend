import unittest

import numpy as np
from numba import njit, prange

from modules.simulation.calc.numba.vector_matrix import dot_product_matrix_vector


class TestNumbaDotProductMatrixVector(unittest.TestCase):
    def case_dot_product_matrix_vector(self, matrix, vector):
        np.testing.assert_equal(dot_product_matrix_vector(matrix, vector), np.dot(matrix, vector))

    def test_dot_product_matrix_vector_3d(self):
        self.case_dot_product_matrix_vector(
            np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]), np.array([2, 2, 2])
        )
        self.case_dot_product_matrix_vector(
            np.array([[-1, -1, -1], [-1, -1, -1], [-1, -1, -1]]), np.array([2, 2, 2])
        )
        self.case_dot_product_matrix_vector(
            np.array([[-1, -1, -1], [1, 1, 1], [-1, -1, -1]]), np.array([2, 2, 2])
        )
        self.case_dot_product_matrix_vector(
            np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]), np.array([2, 2, 2])
        )

    def test_dot_product_matrix_vector_invalid_inputs(self):
        with self.assertRaises(ValueError):
            self.case_dot_product_matrix_vector(
                np.array([[1, 1], [1, 1, 1], [1, 1, 1]]), np.array([2, 2, 2])
            )

        with self.assertRaises(ValueError):
            self.case_dot_product_matrix_vector(
                np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]), np.array([2, 2])
            )

        with self.assertRaises(ValueError):
            self.case_dot_product_matrix_vector(
                np.array([[1, 1, 1, 1], [1, 1, 1], [1, 1, 1]]), np.array([2, 2, 2])
            )

        with self.assertRaises(ValueError):
            self.case_dot_product_matrix_vector(
                np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]), np.array([2, 2, 2, 2])
            )

    def test_dot_product_matrix_vector_njit(self):
        """Tests if the function is callable from numba njit compiled function"""

        matrix = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])

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
                dot_product_matrix_vector(matrix, vector)

        @njit(parallel=True)
        def function_njit_parallel():
            for i in prange(vectors.shape[0]):  # pylint: disable=not-an-iterable
                dot_product_matrix_vector(matrix, vectors[i])

        function_njit()
        function_njit_parallel()
