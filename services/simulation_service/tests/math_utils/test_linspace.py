
import numpy as np
import pytest

from math_utils.linspace import linspace_numba


@pytest.mark.parametrize(
    "start,end,num",
    [
        # Integer ranges
        (0, 10, 1),
        (0, 10, 2),
        (0, 10, 3),
        (0, 10, 1000),
        (10, 0, 3),  # Reversed range
        # Float ranges
        (0.5, 10.0, 1),
        (0.5, 10.0, 2),
        (0.5, 10.0, 3),
        (0.5, 1.5, 5),
        (-1.0, 1.0, 5),  # Negative to positive range
        (10.5, 10.5, 5),  # Identical start and end
        # Large ranges
        (-1e9, 1e9, 3),
        (0, 1e9, 10),
        # Small ranges
        (0, 1e-9, 5),
        # Negative ranges
        (-10, 0, 5),
        (-10, -1, 5),
        (-10, -10, 1),
        # num = 0
        (0, 10, 0),
        # Large number of points
        (0, 10, 1_000_000),
        # Precision test
        (1e-10, 1e-9, 5),
    ],
)
def test_linspace_matches_numpy(start, end, num):
    x = linspace_numba(start, end, num)
    y = np.linspace(start, end, num)
    np.testing.assert_array_equal(x, y)
