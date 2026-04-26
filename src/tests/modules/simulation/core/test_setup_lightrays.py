import unittest
from typing import List
import numpy as np

from backend.src.custom_types.vector import Vector
from backend.src.custom_types.plane import Plane
from backend.src.custom_types.lightsource_parameters import LightsourceParameters
from backend.src.custom_types.spectrum import Spectrum
from backend.src.modules.simulation.constants.units import MILLI_METERS
from backend.src.modules.simulation.core.setup_lightrays import setup_lightrays


class TestAllocLightrays(unittest.TestCase):
    def setUp(self):
        self.spectrum = Spectrum(
            name="Test", wavelengths=[450, 550], intensities=[0.01, 0.02]
        )

        self.lightsource = LightsourceParameters(
            direction_vector=Vector.from_list([1, 0, 0]),
            support_vector=Vector.from_list([0, 0, 0]),
            gap_height_meters=1 * MILLI_METERS,
            count_rays_height=10,
            gap_width_meters=3 * MILLI_METERS,
            count_rays_width=10,
            ray_divergence_degrees=1,
            count_diverging_rays=10,
        )

        self.planes: List[Plane] = [
            Plane(
                normal_vector=Vector.from_list([0.5, -0.5, 0.0]),
                support_vector=Vector.from_list([1.0, 1.0, 0.0]),
            ),
            Plane(
                normal_vector=Vector.from_list([0.5, 0.5, 0.0]),
                support_vector=Vector.from_list([1.0, 1.0, 0.0]),
            ),
        ]

        self.lightray_count = (
            len(self.spectrum.wavelengths)
            * self.lightsource.count_rays_height
            * self.lightsource.count_rays_width
            * self.lightsource.count_diverging_rays
        )

        self.plane_count = len(self.planes)

        (
            self.direction_vectors,
            self.support_vectors,
            self.wavelengths,
            self.intensities,
        ) = setup_lightrays(
            spectrum=self.spectrum, lightsource=self.lightsource, planes=self.planes
        )

    def test_setup_lightrays_count(self):
        # check first dimension equals count of lightrays
        self.assertEqual(self.direction_vectors.shape[0], self.lightray_count)
        self.assertEqual(self.support_vectors.shape[0], self.lightray_count)
        self.assertEqual(self.wavelengths.shape[0], self.lightray_count)
        self.assertEqual(self.intensities.shape[0], self.lightray_count)

        # check second dimension equals plane count + 1 for initial values
        self.assertEqual(self.direction_vectors.shape[1], self.plane_count + 1)
        self.assertEqual(self.support_vectors.shape[1], self.plane_count + 1)
        self.assertEqual(self.intensities.shape[1], self.plane_count + 1)

    def test_origin_height(self):
        spectrum = Spectrum(name="Test", wavelengths=[450], intensities=[0.01])

        lightsource = LightsourceParameters(
            direction_vector=Vector.from_list([1, 0, 0]),
            support_vector=Vector.from_list([1, 1, 1]),
            gap_height_meters=1 * MILLI_METERS,
            count_rays_height=3,
            gap_width_meters=3 * MILLI_METERS,
            count_rays_width=1,
            ray_divergence_degrees=1,
            count_diverging_rays=10,
        )

        planes: List[Plane] = [
            Plane(
                normal_vector=Vector.from_list([0.5, -0.5, 0.0]),
                support_vector=Vector.from_list([1.0, 1.0, 0.0]),
            ),
            Plane(
                normal_vector=Vector.from_list([0.5, 0.5, 0.0]),
                support_vector=Vector.from_list([1.0, 1.0, 0.0]),
            ),
        ]

        (
            _,
            support_vectors,
            _,
            _,
        ) = setup_lightrays(spectrum=spectrum, lightsource=lightsource, planes=planes)

        self.assertEqual(lightsource.count_rays_height, 3)
        np.testing.assert_array_equal(
            support_vectors[0, 0],
            lightsource.support_vector.to_numpy_array()
            + np.array([0, 0, -lightsource.gap_height_meters / 2]),
        )
        np.testing.assert_array_equal(
            support_vectors[1, 0], lightsource.support_vector.to_numpy_array()
        )
        np.testing.assert_array_equal(
            support_vectors[2, 0],
            lightsource.support_vector.to_numpy_array()
            + np.array([0, 0, lightsource.gap_height_meters / 2]),
        )

    def test_origin_width(self):
        spectrum = Spectrum(name="Test", wavelengths=[450], intensities=[0.01])

        lightsource = LightsourceParameters(
            direction_vector=Vector.from_list([1, 0, 0]),
            support_vector=Vector.from_list([1, 1, 1]),
            gap_height_meters=1 * MILLI_METERS,
            count_rays_height=1,
            gap_width_meters=3 * MILLI_METERS,
            count_rays_width=3,
            ray_divergence_degrees=1,
            count_diverging_rays=10,
        )

        planes: List[Plane] = [
            Plane(
                normal_vector=Vector.from_list([0.5, -0.5, 0.0]),
                support_vector=Vector.from_list([1.0, 1.0, 0.0]),
            ),
            Plane(
                normal_vector=Vector.from_list([0.5, 0.5, 0.0]),
                support_vector=Vector.from_list([1.0, 1.0, 0.0]),
            ),
        ]

        (
            _,
            support_vectors,
            _,
            _,
        ) = setup_lightrays(spectrum=spectrum, lightsource=lightsource, planes=planes)

        self.assertEqual(lightsource.count_rays_width, 3)
        np.testing.assert_array_equal(
            support_vectors[0, 0],
            lightsource.support_vector.to_numpy_array()
            + np.array([0, -lightsource.gap_width_meters / 2, 0]),
        )
        np.testing.assert_array_equal(
            support_vectors[1, 0], lightsource.support_vector.to_numpy_array()
        )
        np.testing.assert_array_equal(
            support_vectors[2, 0],
            lightsource.support_vector.to_numpy_array()
            + np.array([0, lightsource.gap_width_meters / 2, 0]),
        )
