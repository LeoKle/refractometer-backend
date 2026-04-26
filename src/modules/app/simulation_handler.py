import threading
import time
import datetime

from interfaces.app.simulation_interface import ISimulation
from interfaces.database.database_interface import IDatabase
from interfaces.app.simulation_handler import ISimulationHandler

from custom_types.simulation_result import SimulationResult


class SimulationHandler(ISimulationHandler):
    def __init__(self, simulation: ISimulation, database: IDatabase):
        super().__init__(simulation, database)
        self.is_running = True
        self.thread = threading.Thread(target=self.process_queue)
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.thread.join()

    def process_queue(self):
        while self.is_running:
            print("Running queue")
            # get element from db
            simulation = self.database.simulation_queue_service().find_next_simulation()

            # no simulation queued
            if not simulation:
                time.sleep(5)
                continue

            # set being_processed to true
            simulation.being_processed = True
            self.database.simulation_queue_service().update_queued_simulation(
                simulation
            )

            # setup planes, simulate, simulate detector
            self.simulation.set_parameters(simulation.parameters)
            self.simulation.simulate()
            image = self.simulation.get_detector_image()

            image_id = self.database.image_service().save_image(image)

            result = SimulationResult(
                name=simulation.name,
                parameters=simulation.parameters,
                image_id=str(image_id),
                issued_at=simulation.issued_at,
                completed_at=datetime.datetime.now(),
            )

            # delete element from queue DB, add to result DB
            self.database.simulation_result_service().save_result(result)
            self.database.simulation_queue_service().delete_queued_simulation(
                simulation.id
            )

            if simulation.callback_url:
                print("Callback to invoke found")

    def get_state(self):
        pass
