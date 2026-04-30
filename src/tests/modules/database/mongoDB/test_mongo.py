import unittest

from interfaces.database.database_interface import IDatabase
from interfaces.database.services.image_service_interface import IImageService
from interfaces.database.services.sample_service_interface import ISampleService
from interfaces.database.services.simulation_queue_service_interface import (
    ISimulationQueueService,
)
from interfaces.database.services.simulation_result_service_interface import (
    ISimulationResultService,
)
from interfaces.database.services.spectrum_service_interface import ISpectrumService
from modules.mongoDB.mongo_db import MongoDB


class TestMongoDB(unittest.TestCase):
    """Test the MongoDB implementation of IDatabase"""

    def setUp(self):
        self.database = MongoDB()

    def test_init(self):
        self.assertIsInstance(self.database, IDatabase)

    def test_spectrum_service(self):
        spectrum_service = self.database.spectrum_service()
        self.assertIsInstance(spectrum_service, ISpectrumService)

    def test_sample_service(self):
        sample_service = self.database.sample_service()
        self.assertIsInstance(sample_service, ISampleService)

    def test_simulation_result_service(self):
        simulation_result_service = self.database.simulation_result_service()
        self.assertIsInstance(simulation_result_service, ISimulationResultService)

    def test_simulation_queue_service(self):
        simulation_queue_service = self.database.simulation_queue_service()
        self.assertIsInstance(simulation_queue_service, ISimulationQueueService)

    def test_image_service(self):
        image_service = self.database.image_service()
        self.assertIsInstance(image_service, IImageService)
