from typing import List
import unittest
import numpy as np

from backend.src.custom_types.detector_calibration import WavelengthCalibration
from backend.src.custom_types.detector_parameters import DetectorParameters
from backend.src.custom_types.plane import Plane, PlaneGeometry
from backend.src.custom_types.lightsource_parameters import LightsourceParameters
from backend.src.custom_types.sample import Sample
from backend.src.custom_types.spectrum import Spectrum
from backend.src.custom_types.vector import Vector
from backend.src.custom_types.simulation_parameters import SimulationParameters
from backend.src.modules.simulation.simulation import Simulation
from backend.src.modules.simulation.calc.physics.refraction import refracted_direction_vector
from backend.src.modules.simulation.calc.physics.sellmeier import sellmeier_equation
from backend.src.modules.simulation.constants.units import DEGREES, NANO_METERS
from backend.src.modules.simulation.calc.numba.vector import rotate_vector_3d

ENTRY_ANGLE = 40
ANGLE_PRISM = 60


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.lightsource = LightsourceParameters(
            direction_vector=Vector.from_list([1, 0, 0]),
            support_vector=Vector.from_list([0, 0, 0]),
            gap_height_meters=1,
            count_rays_height=1,
            gap_width_meters=1,
            count_rays_width=1,
            ray_divergence_degrees=1,
            count_diverging_rays=1,
        )

        self.spectrum = Spectrum(
            name="Calibration Wavelength",
            wavelengths=[450],
            intensities=[1],
        )

        # NBK-7
        b = (1.03961212, 0.231792344, 1.01046945)
        c = (6.00069867 * 10**-3, 2.00179144 * 10**-2, 103.560653)

        self.sample = Sample(name="NKB-7", sellmeier_coefficients={"B": b, "C": c})

        self.planes = PlaneGeometry(
            base_vector=Vector.from_list([1, 0, 0]),
            entry_angle=ENTRY_ANGLE,
            prism_angle=ANGLE_PRISM,
            distance1=13.5e-2,
            distance2=14.5e-2,
        )

        self.detector = DetectorParameters(
            distance3=8.5e-2,
            normal_vector=WavelengthCalibration(wavelength=632.8 * NANO_METERS),
            height_pixels=2556,
            width_pixels=2440,
            pixel_size_meters_per_pixel=5e-6,
        )

        self.simulation_parameters = SimulationParameters(
            lightsource=self.lightsource,
            spectrum=self.spectrum,
            sample=self.sample,
            planes=self.planes,
            detector=self.detector,
        )

    def test_class(self):
        wavelength = self.detector.normal_vector.wavelength

        b = self.sample.sellmeier_coefficients.B
        c = self.sample.sellmeier_coefficients.C

        direction_vector = self.lightsource.direction_vector.to_numpy_array()

        normal_vector_1 = rotate_vector_3d(
            direction_vector, 0, 0, -self.planes.entry_angle * DEGREES
        )

        refractive_index_air = 1.000293
        refractive_index = sellmeier_equation(b, c, wavelength)

        direction_vector_1 = refracted_direction_vector(
            refractive_index_air, refractive_index, direction_vector, normal_vector_1
        )

        # second refraction

        normal_vector_2 = rotate_vector_3d(
            normal_vector_1, 0, 0, self.planes.prism_angle * DEGREES
        )

        direction_vector_2 = refracted_direction_vector(
            refractive_index, refractive_index_air, direction_vector_1, normal_vector_2
        )

        # testing sim class

        sim_instance = Simulation()

        print("NV1", normal_vector_1)
        print("NV2", normal_vector_2)
        print("DV1", direction_vector_1)
        print("DV2", direction_vector_2)

        # test plane setup

        planes: List[Plane] = sim_instance.setup_planes(self.planes)
        print(planes)

        # test plane normal vectors
        np.testing.assert_array_almost_equal(
            normal_vector_1, planes[0].normal_vector.to_numpy_array()
        )
        np.testing.assert_array_almost_equal(
            normal_vector_2, planes[1].normal_vector.to_numpy_array()
        )

        # TODO: test calibration of detector
        detector_nv, detector_sv = sim_instance.calibrate_detector(
            self.simulation_parameters
        )

        print(detector_nv, detector_sv)

        # test,

    def test_simulation(self):
        lightsource = LightsourceParameters(
            direction_vector=Vector.from_list([1, 0, 0]),
            support_vector=Vector.from_list([0, 0, 0]),
            gap_height_meters=10e-3,
            count_rays_height=5,
            gap_width_meters=3e-3,
            count_rays_width=5,
            ray_divergence_degrees=1,
            count_diverging_rays=10,
        )

        wavelengths = np.arange(450e-9, 651e-9, 1e-9)
        spectrum = Spectrum(
            name="Test Spektrum",
            wavelengths=wavelengths,
            intensities=np.linspace(1, 1, len(wavelengths)),
        )

        sim_parameters = SimulationParameters(
            lightsource=lightsource,
            spectrum=spectrum,
            sample=self.sample,
            planes=self.planes,
            detector=self.detector,
        )

        sim_instance = Simulation()

        sim_instance.set_parameters(sim_parameters)
        sim_instance.simulate()

        image = sim_instance.get_detector_image()

        # print(image)
