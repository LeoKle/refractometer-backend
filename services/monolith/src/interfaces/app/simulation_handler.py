from abc import ABC, abstractmethod


class ISimulationHandler(ABC):
    @abstractmethod
    def process_queue(self):
        pass

    @abstractmethod
    def get_state(self):
        pass
