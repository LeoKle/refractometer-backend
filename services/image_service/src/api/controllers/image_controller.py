import uuid
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from api.models.detector_image_dto import DetectorImageDTO, DetectorPostResult
from containers.container import DependencyContainer
from interfaces.image_repository_interface import ImageRepositoryInterface
from models.detector_image import DetectorImage

router = APIRouter(prefix="/api")


@router.get("/image/{image_id}", response_model=DetectorImageDTO)
@inject
def get_image(
    image_id: str,
    image_repo: Annotated[
        ImageRepositoryInterface, Depends(Provide[DependencyContainer.image_repo])
    ],
) -> DetectorImageDTO:
    try:
        image_uuid = uuid.UUID(image_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid UUID: {image_id}"
        ) from None

    try:
        result: DetectorImage = image_repo.get_image(image_uuid)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Image {image_id} not found"
        ) from None

    return DetectorImageDTO(**result.model_dump())


@router.post("/image", status_code=status.HTTP_201_CREATED, response_model=DetectorPostResult)
@inject
def post_image(
    body: DetectorImageDTO,
    image_repo: Annotated[
        ImageRepositoryInterface, Depends(Provide[DependencyContainer.image_repo])
    ],
) -> DetectorPostResult:

    image = DetectorImage(**body.model_dump())

    image_repo.save_image(image)

    return DetectorPostResult(id=str(image.id))
