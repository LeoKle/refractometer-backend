from interfaces.repositories.sample_repository_interface import ISampleRepository
from interfaces.services.sample_service_interface import ISampleService
from models.sample import Sample


class SampleService(ISampleService):
    def __init__(self, repository: ISampleRepository):
        self.repository = repository

    def get_samples(self) -> list[Sample]:
        return self.repository.find_all()

    def load_sample(self, sample_id: str) -> Sample | None:
        return self.repository.find_by_id(sample_id)

    def save_sample(self, sample: Sample):
        self.repository.insert(sample)

    def update_sample(self, sample: Sample):
        self.repository.update(sample)

    def delete_sample(self, sample_id: str):
        self.repository.delete(sample_id)
