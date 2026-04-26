import unittest
import numpy as np
from backend.src.tests.modules.simulation.calc.numba import njit, prange
from backend.src.modules.simulation.calc.physics.sellmeier import sellmeier_equation


class TestSellmeier(unittest.TestCase):
    def test_nbk7(self):
        b = (1.03961212, 0.231792344, 1.01046945)
        c = (0.00600069867, 0.0200179144, 103.560653)

        np.testing.assert_allclose(
            sellmeier_equation(b, c, 632.8e-9), 1.515, rtol=1e-6, atol=1e-3
        )

        np.testing.assert_allclose(
            sellmeier_equation(b, c, 450), 1.811737011, rtol=1e-6, atol=1e-3
        )

        np.testing.assert_allclose(
            sellmeier_equation(b, c, 550), 1.8116892, rtol=1e-6, atol=1e-3
        )

        np.testing.assert_allclose(
            sellmeier_equation(b, c, 650), 1.81166268, rtol=1e-6, atol=1e-3
        )

    def test_fused_silica(self):
        b = (1.5039759, 0.55069141, 6.5927379)
        c = (5.48041129 * 1e-3, 1.47994281 * 1e-2, 402.89514)

        np.testing.assert_allclose(
            sellmeier_equation(b, c, 450e-6), 3.10814227, rtol=1e-6, atol=1e-3
        )

        np.testing.assert_allclose(
            sellmeier_equation(b, c, 550e-6), 3.10744232, rtol=1e-6, atol=1e-3
        )

        np.testing.assert_allclose(
            sellmeier_equation(b, c, 650e-6), 3.10704008, rtol=1e-6, atol=1e-3
        )

    def test_sellmeier_equation_njit(self):
        """Tests that the sellmeier_equation function can also be called by other njit compiled functions"""
        b = (1.03961212, 0.231792344, 1.01046945)
        c = (6.00069867 * 10**-9, 2.00179144 * 10**-8, 1.03560653 * 10**-4)

        wavelength = 450 * 10**-9

        @njit
        def function_njit():
            for _ in range(100):
                sellmeier_equation(b, c, wavelength)

        @njit(parallel=True)
        def function_njit_parallel():
            for _ in prange(10):  # pylint: disable=not-an-iterable
                sellmeier_equation(b, c, wavelength)

        function_njit()
        function_njit_parallel()
