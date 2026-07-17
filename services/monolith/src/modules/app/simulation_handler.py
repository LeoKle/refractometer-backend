import datetime
import threading
import time

from loguru import logger

from custom_types.simulation_result import SimulationResult
from interfaces.app.simulation_handler import ISimulationHandler
from interfaces.app.simulation_interface import ISimulation
from interfaces.database.services.image_service_interface import IImageService
from interfaces.database.services.simulation_result_service_interface import (
    ISimulationResultService,
)
from interfaces.queue_service_interface import QueueServiceInterface


class SimulationHandler(ISimulationHandler):
    def __init__(
        self,
        simulation: ISimulation,
        queue_service: QueueServiceInterface,
        image_service: IImageService,
        simulation_result_service: ISimulationResultService,
    ):
        self.simulation = simulation
        self.queue_service = queue_service
        self.image_service = image_service
        self.simulation_result_service = simulation_result_service

        self.is_running = False
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return

        self.is_running = True
        self.thread = threading.Thread(target=self.process_queue, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()

    def process_queue(self):
        while self.is_running:
            logger.info("Running queue")

            simulation = self.queue_service.claim_element()

            # no simulation queued
            if not simulation:
                time.sleep(5)
                continue

            # setup planes, simulate, simulate detector
            self.simulation.set_parameters(simulation.parameters)
            self.simulation.simulate()
            image = self.simulation.get_detector_image()

            image_id = self.image_service.save_image(image)

            result = SimulationResult(
                name=simulation.name,
                parameters=simulation.parameters,
                image_id=str(image_id),
                issued_at=simulation.issued_at,
                completed_at=datetime.datetime.now(tz=datetime.UTC),
            )

            # delete element from queue DB, add to result DB
            self.simulation_result_service.save_result(result)
            deleted = self.queue_service.delete_queued_element(simulation.id)

            if deleted:
                logger.info("Deleted queued element")
            else:
                logger.info("Couldn't delete queued element")

            if simulation.callback_url:
                logger.info("Callback to invoke found")

    def get_state(self):
        pass
