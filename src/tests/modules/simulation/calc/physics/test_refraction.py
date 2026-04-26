import unittest
import numpy as np
from tests.modules.simulation.calc.numba import njit, prange
import math

from modules.simulation.calc.physics.refraction import refracted_direction_vector


class TestRefraction(unittest.TestCase):
    def snells_law(
        self,
        refractive_index_1,
        refractive_index_2,
        direction_vector_light,
        normal_vector_plane,
    ):
        """Vector form of Snell's Law
        source: ISBN: 978-3-527-62501-7 p. 44"""

        direction_vector_light = direction_vector_light / np.linalg.norm(
            direction_vector_light
        )
        normal_vector_plane = normal_vector_plane / np.linalg.norm(normal_vector_plane)

        index_ratio = refractive_index_1 / refractive_index_2
        nv_dot_dv = np.dot(normal_vector_plane, direction_vector_light)

        first_term = index_ratio * direction_vector_light

        sqrt_term = 1 - index_ratio**2 * (1 - nv_dot_dv**2)
        bracket_term = index_ratio * nv_dot_dv - math.sqrt(sqrt_term)

        second_term = normal_vector_plane * bracket_term

        refracted_vector = first_term - second_term

        return refracted_vector

    def case_refraction(
        self,
        refractive_index_1,
        refractive_index_2,
        direction_vector_light,
        normal_vector_plane,
        desired_direction_vector=None,
    ):
        if desired_direction_vector is None:
            desired_direction_vector = self.snells_law(
                refractive_index_1,
                refractive_index_2,
                direction_vector_light,
                normal_vector_plane,
            )

        np.testing.assert_equal(
            refracted_direction_vector(
                refractive_index_1,
                refractive_index_2,
                direction_vector_light,
                normal_vector_plane,
            ),
            desired_direction_vector,
        )

    def test_refraction(self):
        refractive_index_1 = 1
        refractive_index_2 = 2
        normal_vector = np.array([-1, 0, 0])
        direction_vector = np.array([-1, 0, 0])

        self.case_refraction(
            refractive_index_1, refractive_index_2, direction_vector, normal_vector
        )

    def test_refraction_non_normalized(self):
        # vector should be the same even if vectors are not normalized
        refractive_index_1 = 1
        refractive_index_2 = 2
        normal_vector = np.array([-1, 0, 0])
        direction_vector = np.array([-1, 0, 0])

        desired_vector = self.snells_law(
            refractive_index_1,
            refractive_index_2,
            direction_vector,
            normal_vector,
        )

        self.case_refraction(
            refractive_index_1,
            refractive_index_2,
            direction_vector * 10,
            normal_vector * 5,
            desired_vector,
        )

    def test_refraction_invalid_parameters(self):
        # function should not accept refractive indizies which result in the ratio being less than 0
        refractive_index_1 = 1
        refractive_index_2 = -2
        normal_vector = np.array([-1, 0, 0])
        direction_vector = np.array([-1, 0, 0])

        with np.testing.assert_raises(ValueError):
            refracted_direction_vector(
                refractive_index_1,
                refractive_index_2,
                direction_vector,
                normal_vector,
            )

        refractive_index_1 = -1
        refractive_index_2 = 2
        normal_vector = np.array([-1, 0, 0])
        direction_vector = np.array([-1, 0, 0])

        with np.testing.assert_raises(ValueError):
            refracted_direction_vector(
                refractive_index_1,
                refractive_index_2,
                direction_vector,
                normal_vector,
            )

        refractive_index_1 = 0
        refractive_index_2 = 2
        normal_vector = np.array([-1, 0, 0])
        direction_vector = np.array([-1, 0, 0])

        with np.testing.assert_raises(ValueError):
            refracted_direction_vector(
                refractive_index_1,
                refractive_index_2,
                direction_vector,
                normal_vector,
            )

        refractive_index_1 = 1
        refractive_index_2 = 0
        normal_vector = np.array([-1, 0, 0])
        direction_vector = np.array([-1, 0, 0])

        with np.testing.assert_raises(ValueError):
            refracted_direction_vector(
                refractive_index_1,
                refractive_index_2,
                direction_vector,
                normal_vector,
            )

        refractive_index_1 = -1
        refractive_index_2 = -2
        normal_vector = np.array([-1, 0, 0])
        direction_vector = np.array([-1, 0, 0])

        with np.testing.assert_raises(ValueError):
            refracted_direction_vector(
                refractive_index_1,
                refractive_index_2,
                direction_vector,
                normal_vector,
            )

    def test_dot_product_matrix_vector_njit(self):
        """Tests if the function is callable from numba njit compiled function"""

        refractive_index_1 = 1
        refractive_index_2 = 2
        normal_vector = np.array([-1, 0, 0])
        direction_vector = np.array([-1, 0, 0])

        @njit
        def function_njit():
            refracted_direction_vector(
                refractive_index_1,
                refractive_index_2,
                direction_vector,
                normal_vector,
            )

        @njit(parallel=True)
        def function_njit_parallel():
            for _ in prange(10):  # pylint: disable=not-an-iterable
                refracted_direction_vector(
                    refractive_index_1,
                    refractive_index_2,
                    direction_vector,
                    normal_vector,
                )

        function_njit()
        function_njit_parallel()
