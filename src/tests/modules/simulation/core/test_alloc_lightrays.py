import unittest
from typing import List

from backend.src.custom_types.vector import Vector
from backend.src.custom_types.plane import Plane
from backend.src.custom_types.lightsource_parameters import LightsourceParameters
from backend.src.custom_types.spectrum import Spectrum
from backend.src.modules.simulation.constants.units import MILLI_METERS
from backend.src.modules.simulation.core.alloc_lightrays import alloc_arrays


class TestAllocLightrays(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spectrum = Spectrum(
            name="Test", wavelengths=[450, 550], intensities=[0.01, 0.02]
        )

        cls.lightsource = LightsourceParameters(
            direction_vector=Vector.from_list([1, 0, 0]),
            support_vector=Vector.from_list([1, 1, 1]),
            gap_height_meters=1 * MILLI_METERS,
            count_rays_height=3,
            gap_width_meters=3 * MILLI_METERS,
            count_rays_width=10,
            ray_divergence_degrees=1,
            count_diverging_rays=10,
        )

        cls.planes: List[Plane] = [
            Plane(
                normal_vector=Vector.from_list([0.5, -0.5, 0.0]),
                support_vector=Vector.from_list([1.0, 1.0, 0.0]),
            ),
            Plane(
                normal_vector=Vector.from_list([0.5, 0.5, 0.0]),
                support_vector=Vector.from_list([1.0, 1.0, 0.0]),
            ),
        ]

        cls.lightray_count = (
            len(cls.spectrum.wavelengths)
            * cls.lightsource.count_rays_height
            * cls.lightsource.count_rays_width
            * cls.lightsource.count_diverging_rays
        )

        cls.plane_count = len(cls.planes)

        cls.direction_vectors, cls.support_vectors, cls.wavelengths, cls.intensities = (
            alloc_arrays(cls.lightray_count, cls.plane_count)
        )

    def test_alloc_arrays_count(self):
        # check first dimension equals count of lightrays
        self.assertEqual(self.direction_vectors.shape[0], self.lightray_count)
        self.assertEqual(self.support_vectors.shape[0], self.lightray_count)
        self.assertEqual(self.wavelengths.shape[0], self.lightray_count)
        self.assertEqual(self.intensities.shape[0], self.lightray_count)

        # check second dimension equals plane count + 1 for initial values
        self.assertEqual(self.direction_vectors.shape[1], self.plane_count + 1)
        self.assertEqual(self.support_vectors.shape[1], self.plane_count + 1)
        self.assertEqual(self.intensities.shape[1], self.plane_count + 1)
