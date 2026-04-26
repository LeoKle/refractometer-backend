import unittest
from typing import List
import numpy as np

from modules.simulation.calc.numba.linspace import linspace_numba


class TestLinspace(unittest.TestCase):
    def case(self, start, end, num):
        x = linspace_numba(start, end, num)
        y = np.linspace(start, end, num)
        np.testing.assert_array_equal(x, y)

    def test_linspace_int(self):
        self.case(0, 10, 1)
        self.case(0, 10, 2)
        self.case(0, 10, 3)
        self.case(0, 10, 1000)
        self.case(10, 0, 3)  # Reversed range

    def test_linspace_float(self):
        self.case(0.5, 10.0, 1)
        self.case(0.5, 10.0, 2)
        self.case(0.5, 10.0, 3)
        self.case(0.5, 1.5, 5)
        self.case(-1.0, 1.0, 5)  # Negative to positive range
        self.case(10.5, 10.5, 5)  # Identical start and end

    def test_linspace_large_range(self):
        self.case(-1e9, 1e9, 3)  # Large range with only 3 steps
        self.case(0, 1e9, 10)  # Large positive range

    def test_linspace_small_range(self):
        self.case(0, 1e-9, 5)  # Small range

    def test_linspace_negative_range(self):
        self.case(-10, 0, 5)  # Negative to zero
        self.case(-10, -1, 5)  # Negative range
        self.case(-10, -10, 1)  # Single value, negative start == stop

    def test_linspace_num_zero(self):
        x = linspace_numba(0, 10, 0)
        y = np.linspace(0, 10, 0)
        np.testing.assert_array_equal(x, y)

    def test_linspace_large_num(self):
        self.case(0, 10, 1000000)  # Test with a large number of points

    def test_linspace_precision(self):
        self.case(1e-10, 1e-9, 5)  # Testing precision with small floats
