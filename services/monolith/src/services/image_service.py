import httpx
from pydantic import BaseModel

from custom_types.detector_image import DetectorImage
from interfaces.database.services.image_service_interface import IImageService


class ImageService(IImageService):
    """an implementation of the image service using the Branch-By-Abstraction pattern"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    class SaveImageResultDTO(BaseModel):
        id: str

    def save_image(self, detector_image: DetectorImage) -> str:
        response = httpx.post(self.base_url + "/api/image", json=detector_image.model_dump())

        return response.json()["id"]
