import uuid
from abc import ABC, abstractmethod

from models.detector_image import DetectorImage


class ImageRepositoryInterface(ABC):
    @abstractmethod
    def get_image(self, id: uuid.UUID): ...

    @abstractmethod
    def save_image(self, detector_image: DetectorImage): ...
