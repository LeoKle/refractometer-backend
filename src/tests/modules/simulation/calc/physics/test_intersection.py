import unittest
from backend.src.modules.simulation.calc.physics.intersection import (
    calculate_intersection_line_plane,
)
import numpy as np


class TestIntersection(unittest.TestCase):
    # Case 1: Plane and line intersect
    def calc_intersection_case1(self):
        # Test intersection at 90°
        plane_normal_vector1 = np.array([1, 0, 0])
        plane_support_vector = np.array([5, 6, 0])
        line_direction_vector = np.array([1, 1, 0])
        line_support_vector = np.array([0, 0, 0])
        np.testing.assert_allclose(
            calculate_intersection_line_plane(
                plane_normal_vector1,
                plane_support_vector,
                line_direction_vector,
                line_support_vector,
            ),
            np.array([5, 5, 0]),
        )

        plane_normal_vector1 = np.array([-1, 0, 0])
        plane_support_vector = np.array([5, 6, 0])
        line_direction_vector = np.array([1, 1, 0])
        line_support_vector = np.array([0, 0, 0])
        np.testing.assert_allclose(
            calculate_intersection_line_plane(
                plane_normal_vector1,
                plane_support_vector,
                line_direction_vector,
                line_support_vector,
            ),
            np.array([5, 5, 0]),
        )

        plane_normal_vector1 = np.array([0, 1, 0])
        plane_support_vector = np.array([5, 6, 0])
        line_direction_vector = np.array([1, 1, 0])
        line_support_vector = np.array([0, 0, 0])
        np.testing.assert_allclose(
            calculate_intersection_line_plane(
                plane_normal_vector1,
                plane_support_vector,
                line_direction_vector,
                line_support_vector,
            ),
            np.array([6, 6, 0]),
        )

        # Test intersection with angled
        plane_normal_vector1 = np.array([0.965, -0.258, 0])
        plane_support_vector = np.array([5, 6, 0])
        line_direction_vector = np.array([1, 1, 0])
        line_support_vector = np.array([0, 0, 0])

        np.testing.assert_allclose(
            calculate_intersection_line_plane(
                plane_normal_vector1,
                plane_support_vector,
                line_direction_vector,
                line_support_vector,
            ),
            np.array([4.6339, 4.6339, 0]),
            0.0001,
            0.1,
        )

    # Case 2: Plane and line are parallel to each other
    def calc_intersection_case2(self):
        plane_normal_vector1 = np.array([1, 0, 0])
        plane_support_vector = np.array([1, 1, 0])
        line_direction_vector = np.array([0, 1, 0])
        line_support_vector = np.array([0, 0, 0])

        with np.testing.assert_raises(ValueError):
            calculate_intersection_line_plane(
                plane_normal_vector1,
                plane_support_vector,
                line_direction_vector,
                line_support_vector,
            )

        plane_normal_vector1 = np.array([0, 1, 0])
        plane_support_vector = np.array([1, 1, 0])
        line_direction_vector = np.array([1, 0, 0])
        line_support_vector = np.array([0, 0, 0])

        with np.testing.assert_raises(ValueError):
            calculate_intersection_line_plane(
                plane_normal_vector1,
                plane_support_vector,
                line_direction_vector,
                line_support_vector,
            )

        plane_normal_vector1 = np.array([0, 0, 1])
        plane_support_vector = np.array([5, 5, 5])
        line_direction_vector = np.array([1, 1, 0])
        line_support_vector = np.array([-1, -1, -1])

        with np.testing.assert_raises(ValueError):
            calculate_intersection_line_plane(
                plane_normal_vector1,
                plane_support_vector,
                line_direction_vector,
                line_support_vector,
            )

    # Case 3: Line is within the plane
    def calc_intersection_case3(self):
        plane_normal_vector1 = np.array([0, 1, 0])
        plane_support_vector = np.array([1, 1, 0])
        line_direction_vector = np.array([1, 0, 0])
        line_support_vector = plane_support_vector

        with np.testing.assert_raises(ValueError):
            calculate_intersection_line_plane(
                plane_normal_vector1,
                plane_support_vector,
                line_direction_vector,
                line_support_vector,
            )

        plane_normal_vector1 = np.array([0, -1, 0])
        plane_support_vector = np.array([5, 5, 5])
        line_direction_vector = np.array([1, 0, 1])
        line_support_vector = np.array([5, 5, 5])

        with np.testing.assert_raises(ValueError):
            calculate_intersection_line_plane(
                plane_normal_vector1,
                plane_support_vector,
                line_direction_vector,
                line_support_vector,
            )

    def test_calc_intersection(self):
        self.calc_intersection_case1()
        self.calc_intersection_case2()
        self.calc_intersection_case3()
