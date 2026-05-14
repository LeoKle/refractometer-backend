from abc import ABC, abstractmethod

from models.sample import Sample


class ISampleRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[Sample]:
        """Returns all samples"""

    @abstractmethod
    def find_by_id(self, sample_id: str) -> Sample | None:
        pass

    @abstractmethod
    def insert(self, sample: Sample):
        pass

    @abstractmethod
    def update(self, sample: Sample):
        pass

    @abstractmethod
    def delete(self, sample_id: str):
        pass
