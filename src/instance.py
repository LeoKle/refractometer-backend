from backend.src.modules.app.simulation_handler import SimulationHandler
from backend.src.modules.simulation.simulation import Simulation
from backend.src.modules.app.refractometer_app import RefractometerApp
from backend.src.modules.mongoDB.mongo_db import MongoDB

database = MongoDB()
simulation = Simulation()
simulation_handler = SimulationHandler(simulation=simulation, database=database)

refractometer_app_instance = RefractometerApp(
    simulation_handler=simulation_handler, database=database
)
