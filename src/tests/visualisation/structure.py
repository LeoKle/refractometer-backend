"""Helper functions to display the simulated structure"""

import numpy as np
from matplotlib import pyplot as plt


def visualise_structure(
    direction_vectors,
    support_vectors,
    plane_normal_vectors,
    plane_support_vectors,
):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    plot_points(ax, support_vectors[:, 2])
    # plot_line(ax, support_vectors[:, 0], support_vectors[:, 1])

    # trace lightrays:
    colors = ["r", "lightblue", "blue"]
    for section in range(direction_vectors.shape[1]):
        if section < direction_vectors.shape[1] - 1:
            plot_line(
                ax,
                support_vectors[:, section],
                support_vectors[:, section + 1],
                color=colors[section],
            )
        else:
            plot_vectors(
                ax,
                direction_vectors[:, section],
                support_vectors[:, section],
                color=colors[section],
            )

    # plot planes:
    plot_planes(ax, plane_normal_vectors, plane_support_vectors)

    # plot settings:
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    # ax.view_init(elev=0, azim=0)
    # ax.view_init(elev=0, azim=90)

    fig.savefig("Structure.png")


def plot_planes(ax, plane_normal_vectors, plane_support_vectors):
    z_unit_vector = np.array([0, 0, 1])

    for plane_index in range(len(plane_normal_vectors)):
        span_vector_xy = np.cross(plane_normal_vectors[plane_index], z_unit_vector)

        norm_span_vector = span_vector_xy / np.linalg.norm(span_vector_xy)

        plot_vectors(ax, [norm_span_vector * 0.05], [plane_support_vectors[plane_index]])


def plot_points(ax, points, color="red"):
    for point in points:
        ax.plot(point[0], point[1], point[2], c=color, marker="x")


def plot_line(ax, start_points, end_points, color="green"):
    for start_point, end_point in zip(start_points, end_points):
        ax.plot(
            [
                start_point[0],
                end_point[0],
            ],
            [
                start_point[1],
                end_point[1],
            ],
            [
                start_point[2],
                end_point[2],
            ],
            c=color,
        )


def plot_vectors(ax, direction_vectors, support_vectors, color="black"):
    """Plots the vectors by plotting a line from the support vector to the point,
    which is the sum of the support_vector + direction_vector"""

    for start_point, direction in zip(support_vectors, direction_vectors):
        ax.plot(
            [
                start_point[0],
                start_point[0] + direction[0],
            ],
            [
                start_point[1],
                start_point[1] + direction[1],
            ],
            [
                start_point[2],
                start_point[2] + direction[2],
            ],
            c=color,
        )
