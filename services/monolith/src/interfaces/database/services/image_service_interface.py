from abc import ABC, abstractmethod

from custom_types.detector_image import DetectorImage


class IImageService(ABC):
    @abstractmethod
    def save_image(self, detector_image: DetectorImage) -> str:
        pass

    @abstractmethod
    def retrieve_image(self, image_id: str) -> DetectorImage:
        pass
