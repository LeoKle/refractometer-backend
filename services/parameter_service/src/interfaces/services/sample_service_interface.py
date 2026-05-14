from abc import ABC, abstractmethod

from models.sample import Sample


class ISampleService(ABC):
    @abstractmethod
    def get_samples(self) -> list[Sample]:
        """Returns all samples"""

    @abstractmethod
    def load_sample(self, sample_id: str) -> Sample | None:
        pass

    @abstractmethod
    def save_sample(self, sample: Sample):
        pass

    @abstractmethod
    def update_sample(self, sample: Sample):
        pass

    @abstractmethod
    def delete_sample(self, sample_id: str):
        pass
