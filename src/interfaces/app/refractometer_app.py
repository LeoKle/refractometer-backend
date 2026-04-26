from abc import ABC

from backend.src.interfaces.app.simulation_handler import ISimulationHandler
from backend.src.interfaces.database.database_interface import IDatabase


class IRefractometerApp(ABC):
    def __init__(self, simulation_handler: ISimulationHandler, database: IDatabase):
        self.simulation_handler = simulation_handler
        self.database = database
