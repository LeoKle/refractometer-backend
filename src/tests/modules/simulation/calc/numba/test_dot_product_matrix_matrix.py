import unittest

import numpy as np
from numba import njit, prange

from modules.simulation.calc.numba.matrix import dot_product_matrix_matrix


class TestNumbaDotProductMatrixVector(unittest.TestCase):
    def case_dot_product_matrix_matrix(self, matrix1, matrix2):
        np.testing.assert_equal(
            dot_product_matrix_matrix(matrix1, matrix2), np.dot(matrix1, matrix2)
        )

    def test_dot_product_identity(self):
        """Test multiplication of identity matrices"""
        identity = np.eye(3)
        self.case_dot_product_matrix_matrix(identity, identity)

    def test_dot_product_zeros(self):
        """Test multiplication with matrices containing zeros"""
        matrix1 = np.zeros((2, 3))
        matrix2 = np.zeros((3, 4))
        self.case_dot_product_matrix_matrix(matrix1, matrix2)

        matrix3 = np.zeros((3, 2))
        self.case_dot_product_matrix_matrix(matrix3, matrix1)

    def test_dot_product_simple(self):
        """Test multiplication with simple matrices"""
        matrix1 = np.array([[1, 2, 3], [4, 5, 6]])
        matrix2 = np.array([[7, 8], [9, 10], [11, 12]])
        self.case_dot_product_matrix_matrix(matrix1, matrix2)

    def test_dot_product_invalid_dimensions(self):
        """Test multiplication with matrices of different dimensions"""
        matrix1 = np.array([[1, 2, 3, 4], [4, 5, 6, 7]])
        matrix2 = np.array([[1, 2], [3, 4], [5, 6]])
        with self.assertRaises(ValueError):
            dot_product_matrix_matrix(matrix1, matrix2)

        matrix1 = np.array([[1, 2], [4, 5]])
        matrix2 = np.array([[1, 2], [3, 4], [5, 6]])
        with self.assertRaises(ValueError):
            dot_product_matrix_matrix(matrix1, matrix2)

    def test_dot_product_matrix_vector_njit(self):
        """Tests if the function is callable from numba njit compiled function"""

        matrix1 = np.array([[1, 2, 3], [4, 5, 6]])
        matrix2 = np.array([[7, 8], [9, 10], [11, 12]])

        @njit
        def function_njit():
            dot_product_matrix_matrix(matrix1, matrix2)

        @njit(parallel=True)
        def function_njit_parallel():
            for _ in prange(10):
                dot_product_matrix_matrix(matrix1, matrix2)

        function_njit()
        function_njit_parallel()
