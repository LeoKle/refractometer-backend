import uuid
from abc import ABC, abstractmethod

from models.detector_image import DetectorImage
from models.raw_image import RawImage


class ImageRepositoryInterface(ABC):
    @abstractmethod
    def save_raw(
        self, image_id: uuid.UUID, data: bytes, shape: tuple[int, int], dtype: str
    ) -> None: ...

    @abstractmethod
    def open_raw(self, image_id: uuid.UUID) -> RawImage:
        """Raises FileNotFoundError if the image does not exist."""

    @abstractmethod
    def get_image(self, id: uuid.UUID) -> DetectorImage: ...

    @abstractmethod
    def save_image(self, detector_image: DetectorImage) -> None: ...
