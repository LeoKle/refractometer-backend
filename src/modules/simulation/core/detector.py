import numpy as np
from numba import njit, prange

from modules.simulation.calc.numba.vector import (
    cross_product,
    dot_product_vectors,
    normalize_vector,
)
from modules.simulation.calc.physics.intersection import (
    calculate_intersection_line_plane,
)


@njit(parallel=True, nogil=True)
def calculate_detector_coordinates_3d(
    direction_vectors,
    support_vectors,
    detector_normal_vector,
    detector_support_vector,
):
    """Calculates all intersection with the detector plane and returns them"""
    if direction_vectors.shape[0] != support_vectors.shape[0]:
        raise ValueError("Direction vectors and support vectors do not match in count")

    # calculate detector intersections:
    detector_intersections_3d = np.zeros(
        (direction_vectors.shape[0], 3), dtype=np.float64
    )

    # pylint: disable=not-an-iterable
    for lightray in prange(direction_vectors.shape[0]):
        intersection = calculate_intersection_line_plane(
            detector_normal_vector,
            detector_support_vector,
            direction_vectors[lightray],
            support_vectors[lightray],
        )
        detector_intersections_3d[lightray] = intersection

    return detector_intersections_3d


@njit(parallel=True, nogil=True)
def calculate_detector_coordinates_2d(
    detector_intersections_3d,
    detector_normal_vector,
    detector_support_vector,  # the detector middle point
    y_unit_vector_2d=np.array([0, 0, 1]),
):
    x_unit_vector = cross_product(y_unit_vector_2d, detector_normal_vector)
    y_unit_vector = cross_product(detector_normal_vector, x_unit_vector)

    x_unit_vector = normalize_vector(x_unit_vector)
    y_unit_vector = normalize_vector(y_unit_vector)

    # alloc np array for transformed points
    transformed_points = np.zeros(
        (detector_intersections_3d.shape[0], 2), dtype=np.float64
    )

    # project points onto the plane and transform to 2D coordinates
    # pylint: disable=not-an-iterable
    for intersection in prange(detector_intersections_3d.shape[0]):
        point = detector_intersections_3d[intersection] - detector_support_vector

        x_2d = dot_product_vectors(point, x_unit_vector)
        y_2d = dot_product_vectors(point, y_unit_vector)

        transformed_points[intersection] = [x_2d, y_2d]

    return transformed_points


@njit(parallel=True, nogil=True)
def calculate_detector_image(
    detector_intersections_2d,
    intensities,
    height_pixels=2556,
    width_pixels=2440,
    pixel_size_meters_per_pixel=5e-6,
):
    if detector_intersections_2d.shape[0] != intensities.shape[0]:
        raise ValueError(
            "detector_intersections_2d and intensities do not match in shape"
        )

    print(height_pixels, width_pixels, pixel_size_meters_per_pixel)

    # the detector point is in the bottom right corner
    # we create/move it by assuming the point (0,0) as detector middle point
    br_x = width_pixels * pixel_size_meters_per_pixel / 2
    br_y = height_pixels * pixel_size_meters_per_pixel / 2
    detector_point = np.array([br_x, -br_y])

    image = np.zeros((height_pixels, width_pixels), dtype=np.float64)

    out_of_bounds_count = 0

    # pylint: disable=not-an-iterable
    for intersection in prange(detector_intersections_2d.shape[0]):
        delta_vector = detector_intersections_2d[intersection] - detector_point

        x_delta = delta_vector[0]
        y_delta = delta_vector[1]

        x_pixel = int(-x_delta // pixel_size_meters_per_pixel)
        y_pixel = int(y_delta // pixel_size_meters_per_pixel)

        if (
            x_pixel < 0
            or y_pixel < 0
            or x_pixel >= width_pixels
            or y_pixel >= height_pixels
        ):
            # print(
            #     delta_vector,
            #     x_delta,
            #     y_delta,
            #     x_pixel,
            #     y_pixel,
            #     width_pixels,
            #     height_pixels,
            # )
            # print(
            #     x_pixel < 0,
            #     y_pixel < 0,
            #     x_pixel >= width_pixels,
            #     y_pixel >= height_pixels,
            # )
            out_of_bounds_count += 1
            continue

        image[y_pixel, x_pixel] += intensities[intersection]

    return image, out_of_bounds_count
