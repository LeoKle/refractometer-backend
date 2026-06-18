import numpy as np
from numba import njit, prange

from calc.intersection import calculate_intersection_line_plane
from calc.refraction import refracted_direction_vector
from calc.sellmeier import sellmeier_equation
from constants import DEGREES, REFRACTIVE_INDEX_AIR
from math_utils.linspace import linspace_numba
from math_utils.vector import cross_product, dot_product_vectors, normalize_vector, rotate_vector_3d
from models.lightsource import LightsourceParameters
from models.spectrum import Spectrum
from plots.detector import plot_matrix_as_image
from test_parameters import DETECTOR, LIGHTSOURCE, PLANE_GEOMETRY, PLANES, SAMPLE, SPECTRUM


@njit
def trace_ray(
    initial_support_vector,
    initial_direction_vector,
    wavelength,
    plane_normal_vectors,
    plane_support_vectors,
    b,
    c,
):
    refractive_index = sellmeier_equation(b, c, wavelength)

    support_vector = initial_support_vector
    direction_vector = initial_direction_vector

    for plane in range(plane_normal_vectors.shape[0]):
        intersection = calculate_intersection_line_plane(
            plane_normal_vectors[plane],
            plane_support_vectors[plane],
            direction_vector,
            support_vector,
        )

        support_vector = intersection
        direction_vector = refracted_direction_vector(
            REFRACTIVE_INDEX_AIR if plane == 0 else refractive_index,
            refractive_index if plane == 0 else REFRACTIVE_INDEX_AIR,
            direction_vector,
            plane_normal_vectors[plane],
        )

    return direction_vector, support_vector


@njit(parallel=True)
def trace_batch(
    directions,
    supports,
    wavelengths,
    plane_normal_vectors,
    plane_support_vectors,
    b,
    c,
):
    n = directions.shape[0]

    out_dirs = np.empty((n, 3))
    out_sups = np.empty((n, 3))

    for i in prange(n):
        d, s = trace_ray(
            supports[i],
            directions[i],
            wavelengths[i],
            plane_normal_vectors,
            plane_support_vectors,
            b,
            c,
        )
        out_dirs[i] = d
        out_sups[i] = s

    return out_dirs, out_sups


def generate_lightray_batch(
    spectrum: Spectrum,
    lightsource: LightsourceParameters,
    batch_start: int,
    batch_size: int,
):
    n_angles = lightsource.count_diverging_rays
    n_h = lightsource.count_rays_height
    n_w = lightsource.count_rays_width
    n_spec = len(spectrum.wavelengths)

    angles = (
        [0]
        if n_angles == 1
        else linspace_numba(
            -lightsource.ray_divergence_degrees / 2,
            lightsource.ray_divergence_degrees,
            n_angles,
        )
    )

    shifts_height = (
        [0]
        if n_h == 1
        else linspace_numba(
            -lightsource.gap_height_meters / 2,
            lightsource.gap_height_meters / 2,
            n_h,
        )
    )

    shifts_width = (
        [0]
        if n_w == 1
        else linspace_numba(
            -lightsource.gap_width_meters / 2,
            lightsource.gap_width_meters / 2,
            n_w,
        )
    )

    direction_vector = np.array(lightsource.direction_vector.to_list())
    support_vector = np.array(lightsource.support_vector.to_list())

    batch_end = min(batch_start + batch_size, n_angles * n_h * n_w * n_spec)

    out_dir = []
    out_sup = []
    out_wl = []
    out_int = []

    for i in range(batch_start, batch_end):
        spec_idx = i % n_spec
        tmp = i // n_spec

        w_idx = tmp % n_w
        tmp //= n_w

        h_idx = tmp % n_h
        tmp //= n_h

        a_idx = tmp

        angle = angles[a_idx] * DEGREES
        height_shift = shifts_height[h_idx]
        width_shift = shifts_width[w_idx]

        wavelength = spectrum.wavelengths[spec_idx] * 1e-9  # nm -> meters
        intensity = spectrum.intensities[spec_idx]

        dir_vec = rotate_vector_3d(direction_vector, 0, 0, angle)

        sup_vec = support_vector + np.array([
            0,
            width_shift,
            height_shift,
        ])

        out_dir.append(dir_vec)
        out_sup.append(sup_vec)
        out_wl.append(wavelength)
        out_int.append(intensity)

    return (
        np.array(out_dir),
        np.array(out_sup),
        np.array(out_wl),
        np.array(out_int),
    )


@njit(parallel=True, nogil=True)
def calculate_detector_coordinates_3d(
    direction_vectors,
    support_vectors,
    detector_normal_vector,
    detector_support_vector,
):
    n = direction_vectors.shape[0]
    out = np.empty((n, 3), dtype=np.float64)

    for i in prange(n):
        out[i] = calculate_intersection_line_plane(
            detector_normal_vector,
            detector_support_vector,
            direction_vectors[i],
            support_vectors[i],
        )

    return out


@njit(parallel=True, nogil=True)
def calculate_detector_coordinates_2d(
    detector_intersections_3d,
    detector_normal_vector,
    detector_support_vector,
    y_unit_vector_2d,
):
    n = detector_intersections_3d.shape[0]

    x_unit_vector = cross_product(y_unit_vector_2d, detector_normal_vector)
    y_unit_vector = cross_product(detector_normal_vector, x_unit_vector)

    x_unit_vector = normalize_vector(x_unit_vector)
    y_unit_vector = normalize_vector(y_unit_vector)

    transformed_points = np.empty((n, 2), dtype=np.float64)

    for i in prange(n):
        point = detector_intersections_3d[i] - detector_support_vector

        transformed_points[i, 0] = dot_product_vectors(point, x_unit_vector)
        transformed_points[i, 1] = dot_product_vectors(point, y_unit_vector)

    return transformed_points


@njit(nogil=True)
def calculate_detector_image(
    detector_intersections_2d,
    intensities,
    height_pixels=2556,
    width_pixels=2440,
    pixel_size_meters_per_pixel=5e-6,
):
    n = detector_intersections_2d.shape[0]

    # detector center shift (precomputed, no array allocation)
    br_x = width_pixels * pixel_size_meters_per_pixel * 0.5
    br_y = height_pixels * pixel_size_meters_per_pixel * 0.5

    image = np.zeros((height_pixels, width_pixels), dtype=np.float64)
    out_of_bounds_count = 0

    for i in range(n):
        x = detector_intersections_2d[i, 0] - br_x
        y = detector_intersections_2d[i, 1] + br_y

        x_pixel = int((-x) / pixel_size_meters_per_pixel)
        y_pixel = int(y / pixel_size_meters_per_pixel)

        if x_pixel < 0 or y_pixel < 0 or x_pixel >= width_pixels or y_pixel >= height_pixels:
            out_of_bounds_count += 1
            continue

        image[y_pixel, x_pixel] += intensities[i]

    return image, out_of_bounds_count


if __name__ == "__main__":
    print("Lightsource ", LIGHTSOURCE.model_dump())
    print("Spectrum", SPECTRUM.model_dump())
    print("Sample ", SAMPLE.model_dump())
    print("PlaneGeometry ", PLANE_GEOMETRY.model_dump())
    print("Planes ", PLANES)
    print("Detector ", DETECTOR.model_dump())

    detector_image = np.zeros((DETECTOR.height_pixels, DETECTOR.width_pixels), dtype=np.float64)
    detector_normal_vector, detector_support_vector = (
        np.array([0.76562906, -0.64328232, 0]),
        np.array([0.21007847, -0.054679, 0.0]),
    )
    # detector_normal_vector, detector_support_vector = trace_ray(
    #     np.array([1, 0, 0], dtype=np.float64),
    #     np.array([0, 0, 0], dtype=np.float64),
    #     DETECTOR.normal_vector.wavelength,
    #     plane_normal_vectors,
    #     plane_support_vectors,
    #     b,
    #     c,
    # )

    b = SAMPLE.sellmeier_coefficients.B
    c = SAMPLE.sellmeier_coefficients.C

    plane_normal_vectors = np.array([plane.normal_vector.to_numpy_array() for plane in PLANES])
    plane_support_vectors = np.array([plane.support_vector.to_numpy_array() for plane in PLANES])

    n_angles = LIGHTSOURCE.count_diverging_rays
    n_h = LIGHTSOURCE.count_rays_height
    n_w = LIGHTSOURCE.count_rays_width
    n_spec = len(SPECTRUM.wavelengths)

    total_rays = n_angles * n_h * n_w * n_spec
    batch_size = 50_000
    for start in range(0, total_rays, batch_size):
        dirs, sups, wls, ints = generate_lightray_batch(
            SPECTRUM,
            LIGHTSOURCE,
            start,
            batch_size,
        )

        out_dirs, out_sups = trace_batch(
            dirs,
            sups,
            wls,
            plane_normal_vectors,
            plane_support_vectors,
            b,
            c,
        )

        intersections = calculate_detector_coordinates_3d(
            out_dirs,
            out_sups,
            detector_normal_vector,
            detector_support_vector,
        )

        points_2d = calculate_detector_coordinates_2d(
            intersections,
            detector_normal_vector,
            detector_support_vector,
            np.array([0, 0, 1], dtype=np.float64),
        )

        image, miss = calculate_detector_image(
            points_2d,
            ints,
            height_pixels=DETECTOR.height_pixels,
            width_pixels=DETECTOR.width_pixels,
        )
        detector_image += image

        print(f"Miss ({miss}/{batch_size})")

    plot_matrix_as_image(detector_image)
