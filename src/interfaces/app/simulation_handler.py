from abc import ABC, abstractmethod

from interfaces.app.simulation_interface import ISimulation
from interfaces.database.database_interface import IDatabase


class ISimulationHandler(ABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, simulation: ISimulation, database: IDatabase):
        self.simulation = simulation
        self.database = database

    @abstractmethod
    def process_queue(self):
        pass

    @abstractmethod
    def get_state(self):
        pass
