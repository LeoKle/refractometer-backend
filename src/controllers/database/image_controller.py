from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from containers.container import DependencyContainer
from custom_types.detector_image import DetectorImage
from interfaces.database.services.image_service_interface import IImageService

router = APIRouter()


@router.get("/image/{image_id}")
@inject
def get_result(
    image_id: str,
    image_service: Annotated[
        IImageService, Depends(Provide[DependencyContainer.image_service])
    ],
) -> DetectorImage:
    result = image_service.retrieve_image(image_id)

    return result
