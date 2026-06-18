import copy

import numpy as np

from custom_types.detector_image import DetectorImage
from custom_types.plane import Plane, PlaneGeometry
from custom_types.simulation_parameters import SimulationParameters
from custom_types.simulation_state import SimulationState, SimulationStates
from custom_types.spectrum import Spectrum
from custom_types.vector import Vector
from interfaces.app.simulation_interface import ISimulation
from modules.simulation.calc.numba.vector import rotate_vector_3d
from modules.simulation.calc.physics.sellmeier import sellmeier_equation
from modules.simulation.constants.units import DEGREES
from modules.simulation.core.detector import (
    calculate_detector_coordinates_2d,
    calculate_detector_coordinates_3d,
    calculate_detector_image,
)
from modules.simulation.core.setup_lightrays import setup_lightrays
from modules.simulation.core.simulate_lightrays import simulate_lightrays

# from tests.visualisation.detector import plot_2d_points, plot_matrix_as_image


class Simulation(ISimulation):
    """Test"""

    def __init__(self):
        self._state = SimulationStates.IDLE.value
        self.image = None

    def calibrate_detector(self, simulation_params=SimulationParameters):
        """calibrate the detector normal vector based on a wavelength and set it's support vector"""
        self.detector = simulation_params.detector

        # take the lightsource parameters, but set the total ray count to 1
        self.lightsource = simulation_params.lightsource
        self.lightsource.count_diverging_rays = 1
        self.lightsource.count_rays_height = 1
        self.lightsource.count_rays_width = 1

        self.spectrum = Spectrum(
            name="Calibration",
            wavelengths=[simulation_params.detector.normal_vector.wavelength],
            intensities=[1],
        )
        self.sample = simulation_params.sample

        self.plane_normal_vectors = np.array([
            plane.normal_vector.to_numpy_array() for plane in self.planes
        ])
        self.plane_support_vectors = np.array([
            plane.support_vector.to_numpy_array() for plane in self.planes
        ])
        self.image = None

        self.setup_lightrays()
        self.simulate()

        # the normal vector of the detector is the direction vector
        # of the last lightray
        normal_vector = self.simulated_direction_vectors[-1, -1]
        normal_vector = normal_vector / np.linalg.norm(normal_vector)

        # set the support vector by using the distance from the last support of the plane
        detector_support_vector = (
            normal_vector * simulation_params.detector.distance3
            + self.planes[1].support_vector.to_numpy_array()
        )
        print("Detector NV, SV ", normal_vector, detector_support_vector)
        return normal_vector, detector_support_vector

    def setup_planes(self, plane_params=PlaneGeometry) -> list[Plane]:
        # create the first normal vector by rotation
        normal_vector1 = rotate_vector_3d(
            plane_params.base_vector.to_numpy_array(),
            rotation_radians_x=0,
            rotation_radians_y=0,
            rotation_radians_z=-plane_params.entry_angle * DEGREES,
        )
        # create the second normal vector using the known prism angle
        normal_vector2 = rotate_vector_3d(
            normal_vector1,
            rotation_radians_x=0,
            rotation_radians_y=0,
            rotation_radians_z=plane_params.prism_angle * DEGREES,
        )

        support_vector1 = plane_params.base_vector.to_numpy_array() * plane_params.distance1
        support_vector2 = plane_params.base_vector.to_numpy_array() * plane_params.distance2

        planes = []
        planes.extend((
            Plane(
                normal_vector=Vector.from_list(normal_vector1),
                support_vector=Vector.from_list(support_vector1),
            ),
            Plane(
                normal_vector=Vector.from_list(normal_vector2),
                support_vector=Vector.from_list(support_vector2),
            ),
        ))

        self.planes = planes

        return planes

    def set_parameters(self, simulation_params=SimulationParameters):
        if isinstance(simulation_params.planes, PlaneGeometry):
            self.setup_planes(simulation_params.planes)
        else:
            self.planes = simulation_params.planes

        # check detector parameters
        detector_nv, detector_sv = self.calibrate_detector(copy.deepcopy(simulation_params))

        self.detector.normal_vector = Vector.from_list(detector_nv.tolist())
        self.detector.support_vector = Vector.from_list(detector_sv.tolist())

        self.lightsource = simulation_params.lightsource
        self.spectrum = simulation_params.spectrum
        self.sample = simulation_params.sample

        self.plane_normal_vectors = np.array([
            plane.normal_vector.to_numpy_array() for plane in self.planes
        ])
        self.plane_support_vectors = np.array([
            plane.support_vector.to_numpy_array() for plane in self.planes
        ])
        self.image = None

        self.setup_lightrays()

    def get_state(self) -> SimulationState:
        return self._state

    def setup_lightrays(self):
        self._state = SimulationStates.SETTING_UP.value
        print("Starting setup")

        (
            self.setup_direction_vectors,
            self.setup_support_vectors,
            self.setup_wavelengths,
            self.setup_intensities,
        ) = setup_lightrays(self.spectrum, self.lightsource, self.planes)

        print("Finished setup")
        self._state = SimulationStates.SET_UP.value

    def simulate(self):
        self._state = SimulationStates.SIMULATING.value

        b = self.sample.sellmeier_coefficients.B
        c = self.sample.sellmeier_coefficients.C
        refractive_indices = [
            sellmeier_equation(b, c, self.setup_wavelengths[i])
            for i in range(self.setup_wavelengths.shape[0])
        ]

        (
            self.simulated_direction_vectors,
            self.simulated_support_vectors,
            self.simulated_wavelengths,
            self.simulated_intensities,
        ) = simulate_lightrays(
            self.setup_direction_vectors,
            self.setup_support_vectors,
            self.setup_wavelengths,
            self.setup_intensities,
            self.plane_normal_vectors,
            self.plane_support_vectors,
            refractive_indices,
        )

    def construct_detector_image(self):
        print("Calculating intersections 3d")
        detector_intersections_3d = calculate_detector_coordinates_3d(
            self.simulated_direction_vectors[:, -1],
            self.simulated_support_vectors[:, -1],
            detector_normal_vector=self.detector.normal_vector.to_numpy_array(),
            detector_support_vector=self.detector.support_vector.to_numpy_array(),
        )

        print("Calculating intersections 2d")
        detector_coordinates_2d = calculate_detector_coordinates_2d(
            detector_intersections_3d,
            self.detector.normal_vector.to_numpy_array(),
            self.detector.support_vector.to_numpy_array(),
        )
        print(detector_coordinates_2d)

        br_x = self.detector.width_pixels * self.detector.pixel_size_meters_per_pixel / 2
        br_y = self.detector.height_pixels * self.detector.pixel_size_meters_per_pixel / 2
        detector_point = np.array([br_x, -br_y])
        print("DP", detector_point)

        # plot_2d_points(detector_coordinates_2d, detector_point)

        print("Calculating image")
        detector_image, missed_points = calculate_detector_image(
            detector_coordinates_2d,
            self.simulated_intensities[:, -1],
            height_pixels=self.detector.height_pixels,
            width_pixels=self.detector.width_pixels,
            pixel_size_meters_per_pixel=self.detector.pixel_size_meters_per_pixel,
        )

        min_val = np.min(detector_image)
        max_val = np.max(detector_image)
        detector_image = (detector_image - min_val) / (max_val - min_val)

        # plot_matrix_as_image(detector_image)

        print(f"{missed_points}/{len(detector_coordinates_2d)} lightrays did not hit the detector")

        print("Transforming image")
        self.image = DetectorImage.fromNumpyArray(detector_image)

    def get_detector_image(self) -> DetectorImage:
        # construct detector image
        self._state = SimulationStates.DETECTOR_SIMULATION.value
        self.construct_detector_image()
        self._state = SimulationStates.SIMULATION_DONE.value
        print("Done")

        return self.image
