import numpy as np
import matplotlib.pyplot as plt


def plot_2d_points(points_list, single_point):
    """
    Plots a list of 2D points and a single 2D point on the same plot.

    Args:
    points_list (numpy.ndarray): An array of shape (N, 2) representing N 2D points.
    single_point (numpy.ndarray): A numpy array of shape (2,) representing a single 2D point.
    """
    # Ensure the inputs are numpy arrays
    points_list = np.array(points_list)
    single_point = np.array(single_point)

    # Extract x and y coordinates from the list of 2D points
    x_points = points_list[:, 0]
    y_points = points_list[:, 1]

    # Extract the x and y coordinate of the single point
    x_single = single_point[0]
    y_single = single_point[1]

    # Create the plot
    plt.figure(figsize=(8, 6))

    # Plot the list of 2D points
    plt.scatter(x_points, y_points, color="blue", label="Points List", s=50)

    # Plot the single point with a different color and marker size
    plt.scatter(
        x_single,
        y_single,
        color="red",
        label="Bottom right Point",
        s=100,
        edgecolors="black",
    )

    plt.scatter(
        -x_single,
        -y_single,
        color="red",
        label="Top left Point",
        s=100,
        edgecolors="black",
    )

    # Add labels and a legend
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("2D Points Plot")
    plt.legend()

    # Show the grid for better readability
    plt.grid(True)

    # Display the plot
    plt.savefig("detector.png")


def plot_matrix_as_image(matrix):
    """
    Plots a NumPy 2D matrix as an image where the values represent the color intensity.

    Args:
    matrix (numpy.ndarray): A 2D numpy array representing the matrix.
    """
    plt.figure(figsize=(6, 5))

    # Use imshow to display the matrix as an image with a colormap
    plt.matshow(matrix, cmap="plasma")

    # Invert the y-axis so 0,0 is at the bottom right
    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()

    # Add a colorbar to show the intensity scale
    plt.colorbar(label="Intensity")

    # Add title and axis labels
    plt.title("Matrix as Image")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")

    # Save the image
    plt.savefig("detectorMatrix.png")
