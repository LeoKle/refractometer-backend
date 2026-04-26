import unittest
import numpy as np

from modules.simulation.calc.physics.intersection import (
    calculate_intersection_line_plane,
)
from modules.simulation.core.detector import (
    calculate_detector_coordinates_2d,
    calculate_detector_coordinates_3d,
    calculate_detector_image,
)


class TestDetector(unittest.TestCase):
    def test_3d_intersection_calculation(self):
        """Tests the 3D intersection calculation using a simplified setup"""

    direction_vectors = np.array(
        [
            [1, 0, 0],
            [1, 1, 0],
            [1, 1, 1],
        ]
    )
    support_vectors = np.array(
        [
            [0, 0, 0],
            [5, 0, 0],
            [6, 0, 0],
        ]
    )

    detector_normal_vector = np.array([1, 0, 0])
    detector_support_vector = np.array([5, 0, 0])

    intersections_3d = calculate_detector_coordinates_3d(
        direction_vectors,
        support_vectors,
        detector_normal_vector,
        detector_support_vector,
    )

    for i, intersection in enumerate(intersections_3d):
        np.testing.assert_array_equal(
            intersection,
            calculate_intersection_line_plane(
                detector_normal_vector,
                detector_support_vector,
                direction_vectors[i],
                support_vectors[i],
            ),
        )

    def test_2d_intersection_calculation(self):
        detector_intersections_3d = np.array(
            [
                [1, 5, 5],
                [1, 10, 10],
                [1, -5, 5],
                [1, -10, 10],
                [0, -10, 10],  # offset points will also be projected onto the plane
                [2, -5, 5],
            ]
        )

        detector_normal_vector = np.array([1, 0, 0])
        detector_support_vector = np.array([1, 0, 0])

        expected_results = np.array(
            [
                [5, 5],
                [10, 10],
                [-5, 5],
                [-10, 10],
                [-10, 10],
                [-5, 5],
            ]
        )

        detector_intersections_2d = calculate_detector_coordinates_2d(
            detector_intersections_3d, detector_normal_vector, detector_support_vector
        )

        for expected, actual in zip(expected_results, detector_intersections_2d):
            np.testing.assert_array_equal(expected, actual)

    def test_image_calculation(self):
        # detector params
        height_pixels = 2556
        width_pixels = 2440
        pixel_size_meters_per_pixel = 5e-5

        br_x = width_pixels * pixel_size_meters_per_pixel / 2
        br_y = height_pixels * pixel_size_meters_per_pixel / 2
        detector_point = np.array([br_x, br_y])

        intensity = 0.5
        expected_image = np.full((width_pixels, height_pixels), intensity)

        detector_intersections_2d = np.zeros(
            (height_pixels * width_pixels, 2), dtype=np.float64
        )
        counter = 0
        for width in range(width_pixels):
            for height in range(height_pixels):
                detector_intersections_2d[counter] = detector_point + np.array(
                    [
                        pixel_size_meters_per_pixel / 2
                        + width * pixel_size_meters_per_pixel,
                        pixel_size_meters_per_pixel / 2
                        + height * pixel_size_meters_per_pixel,
                    ]
                )

                counter += 1

        intensities = np.full(width_pixels * height_pixels, intensity)

        detector_image, out_of_bounds_count = calculate_detector_image(
            detector_intersections_2d,
            intensities,
            height_pixels=height_pixels,
            width_pixels=width_pixels,
            pixel_size_meters_per_pixel=pixel_size_meters_per_pixel,
        )

        self.assertEqual(detector_image.shape[0], width_pixels)
        self.assertEqual(detector_image.shape[1], height_pixels)
        self.assertEqual(out_of_bounds_count, 0)
        np.testing.assert_array_equal(expected_image, detector_image)
