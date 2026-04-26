from modules.app.simulation_handler import SimulationHandler
from modules.simulation.simulation import Simulation
from modules.app.refractometer_app import RefractometerApp
from modules.mongoDB.mongo_db import MongoDB

database = MongoDB()
simulation = Simulation()
simulation_handler = SimulationHandler(simulation=simulation, database=database)

refractometer_app_instance = RefractometerApp(
    simulation_handler=simulation_handler, database=database
)
