import uuid
from abc import ABC, abstractmethod

from models.detector_image import DetectorImage
from models.raw_image import RawImage


class ImageRepositoryInterface(ABC):
    @abstractmethod
    def save_raw(
        self,
        image_id: uuid.UUID,
        data: bytes,
        shape: tuple[int, int],
        dtype: str,
        idempotency_key: str | None = None,
    ) -> uuid.UUID:
        """Store an image and return the id it is stored under.

        If an image was already stored with the same idempotency_key, nothing
        is written and the id of the existing image is returned (which may
        differ from image_id).
        """

    @abstractmethod
    def open_raw(self, image_id: uuid.UUID) -> RawImage:
        """Raises FileNotFoundError if the image does not exist."""

    @abstractmethod
    def get_image(self, id: uuid.UUID) -> DetectorImage: ...

    @abstractmethod
    def save_image(
        self, detector_image: DetectorImage, idempotency_key: str | None = None
    ) -> uuid.UUID:
        """Same idempotency semantics as save_raw."""
