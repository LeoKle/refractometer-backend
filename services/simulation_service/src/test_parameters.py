from calc.planegeometry_to_planes import setup_planes
from models.detector import DetectorParameters
from models.lightsource import LightsourceParameters
from models.planes import PlaneGeometry
from models.sample import Sample
from models.spectrum import Spectrum

LIGHTSOURCE = LightsourceParameters(**{
    "direction_vector": {"x": 1, "y": 0, "z": 0},
    "support_vector": {"x": 0, "y": 0, "z": 0},
    "gap_height_meters": 0.01,
    "count_rays_height": 1000,
    "gap_width_meters": 0.0005,
    "count_rays_width": 1000,
    "ray_divergence_degrees": 1,
    "count_diverging_rays": 1000,
})

SPECTRUM = Spectrum(**{
    "name": "TestSpectrum",
    "wavelengths": [450, 500, 550, 600, 650, 700],
    "intensities": [0.6, 0.8, 1.0, 0.9, 0.7, 0.5],
})

SAMPLE = Sample(**{
    "name": "NBK7",
    "sellmeier_coefficients": {
        "B": [1.03961212, 0.231792344, 1.01046945],
        "C": [6.00069867 * 10**-3, 2.00179144 * 10**-2, 103.560653],
    },
})

PLANE_GEOMETRY = PlaneGeometry(**{
    "base_vector": {"x": 1, "y": 0, "z": 0},
    "entry_angle": 40,
    "prism_angle": 60,
    "distance1": 0.135,
    "distance2": 0.145,
})

PLANES = setup_planes(PLANE_GEOMETRY)

DETECTOR = DetectorParameters(**{
    "support_vector": None,
    "distance3": 0.085,
    "normal_vector": {"wavelength": 6.328e-7},
    "height_pixels": 1440,
    "width_pixels": 2560,
    "pixel_size_meters_per_pixel": 0.000003,
})
