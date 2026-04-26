import unittest
import numpy as np
from typing import List

from custom_types.vector import Vector
from custom_types.plane import Plane
from custom_types.lightsource_parameters import LightsourceParameters
from custom_types.spectrum import Spectrum
from modules.simulation.constants.units import MILLI_METERS
from modules.simulation.core.setup_lightrays import setup_lightrays
from modules.simulation.core.simulate_lightrays import simulate_lightrays
from modules.simulation.calc.physics.sellmeier import sellmeier_equation


class TestSimulateLightrays(unittest.TestCase):
    def test_simulate_lightrays(self):
        spectrum = Spectrum(
            name="Test", wavelengths=[450 * 1e-9, 550 * 1e-9], intensities=[0.01, 0.02]
        )

        lightsource = LightsourceParameters(
            direction_vector=Vector.from_list([1, 0, 0]),
            support_vector=Vector.from_list([0, 0, 0]),
            gap_height_meters=1 * MILLI_METERS,
            count_rays_height=10,
            gap_width_meters=3 * MILLI_METERS,
            count_rays_width=10,
            ray_divergence_degrees=1,
            count_diverging_rays=10,
        )

        planes: List[Plane] = [
            Plane(
                normal_vector=Vector.from_list([0.5, -1, 0.0]),
                support_vector=Vector.from_list([0.30, 0, 0.0]),
            ),
            Plane(
                normal_vector=Vector.from_list([1, -0.5, 0.0]),
                support_vector=Vector.from_list([0.36, 0, 0.0]),
            ),
        ]

        setup_direction_vectors, setup_support_vectors, wavelengths, intensities = (
            setup_lightrays(spectrum=spectrum, lightsource=lightsource, planes=planes)
        )

        plane_normal_vectors = np.array(
            [plane.normal_vector.to_list() for plane in planes]
        )
        plane_support_vectors = np.array(
            [plane.support_vector.to_list() for plane in planes]
        )

        b = (1.03961212, 0.231792344, 1.01046945)
        c = (6.00069867 * 10**-9, 2.00179144 * 10**-8, 1.03560653 * 10**-4)

        refractive_indices = [
            sellmeier_equation(b, c, wavelengths[i])
            for i in range(wavelengths.shape[0])
        ]

        (
            simulated_direction_vectors,
            simulated_support_vectors,
            wavelengths,
            intensities,
        ) = simulate_lightrays(
            setup_direction_vectors,
            setup_support_vectors,
            wavelengths,
            intensities,
            plane_normal_vectors,
            plane_support_vectors,
            refractive_indices,
        )

    def test_simulate_lightrays_case1(self):
        """a full simulation case"""
        spectrum = Spectrum(
            name="Test", wavelengths=[450e-9, 550e-9], intensities=[0.01, 0.02]
        )
        lightsource = LightsourceParameters(
            direction_vector=Vector.from_list([1, 0, 0]),
            support_vector=Vector.from_list([0, 0, 0]),
            gap_height_meters=1 * MILLI_METERS,
            count_rays_height=10,
            gap_width_meters=3 * MILLI_METERS,
            count_rays_width=10,
            ray_divergence_degrees=1,
            count_diverging_rays=10,
        )

        planes: List[Plane] = [
            Plane(
                normal_vector=Vector.from_list([0.96592583, 0.0, -0.25881905]),
                support_vector=Vector.from_list([5.0, 0.0, 6.0]),
            ),
            Plane(
                normal_vector=Vector.from_list([0.96592583, 0.0, 0.25881905]),
                support_vector=Vector.from_list([5.0, 0.0, 6.0]),
            ),
        ]

        direction_vectors, support_vectors, wavelengths, intensities = setup_lightrays(
            spectrum=spectrum, lightsource=lightsource, planes=planes
        )

        plane_normal_vectors = np.array(
            [plane.normal_vector.to_list() for plane in planes]
        )
        plane_support_vectors = np.array(
            [plane.support_vector.to_list() for plane in planes]
        )

        b = (1.03961212, 0.231792344, 1.01046945)
        c = (6.00069867 * 10**-9, 2.00179144 * 10**-8, 1.03560653 * 10**-4)

        refractive_indices = [
            sellmeier_equation(b, c, wavelengths[i])
            for i in range(wavelengths.shape[0])
        ]

        direction_vectors, support_vectors, wavelengths, intensities = (
            simulate_lightrays(
                direction_vectors,
                support_vectors,
                wavelengths,
                intensities,
                plane_normal_vectors,
                plane_support_vectors,
                refractive_indices,
            )
        )

        # if there is only one diverging ray:
        # each ray must have the direction vector of the lightsource
        if lightsource.count_diverging_rays == 1:
            for lightray in range(direction_vectors.shape[0]):
                np.testing.assert_array_equal(
                    direction_vectors[lightray, 0],
                    np.array(lightsource.direction_vector),
                )

        # if we only have only ray in height and width:
        # each constructed ray must have the support vector of the lightsource
        if lightsource.count_rays_height == 1 and lightsource.count_rays_width == 1:
            for lightray in range(direction_vectors.shape[0]):
                np.testing.assert_array_equal(
                    support_vectors[lightray, 0],
                    np.array(lightsource.support_vector),
                )
