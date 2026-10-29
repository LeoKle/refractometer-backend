import uuid
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from loguru import logger

from api.models.detector_image_dto import DetectorPostResult
from containers.container import DependencyContainer
from interfaces.image_repository_interface import ImageRepositoryInterface

image_v2_router = APIRouter(prefix="/api/v2", tags=["Image V2"])


def _parse_shape(raw: str) -> tuple[int, int]:
    try:
        rows, cols = (int(x) for x in raw.split(","))
        if rows <= 0 or cols <= 0:
            raise ValueError  # noqa: TRY301

    except ValueError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="X-Image-Shape must look like '2560,2440'",
        ) from None
    else:
        return rows, cols


@image_v2_router.post(
    "/image", status_code=status.HTTP_201_CREATED, response_model=DetectorPostResult
)
@inject
async def post_image_raw(
    request: Request,
    image_repo: Annotated[
        ImageRepositoryInterface, Depends(Provide[DependencyContainer.image_repo])
    ],
    x_image_shape: Annotated[str, Header()] = "2560,2440",
    x_image_dtype: Annotated[str, Header()] = "float32",
) -> DetectorPostResult:
    shape = _parse_shape(x_image_shape)
    data = await request.body()
    image_id = uuid.uuid4()

    try:
        await run_in_threadpool(image_repo.save_raw, image_id, data, shape, x_image_dtype)
    except ValueError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from None

    logger.info("Saved raw image {image_id}", image_id=image_id)
    return DetectorPostResult(id=str(image_id))


@image_v2_router.get("/image/{image_id}")
@inject
def get_image_raw(
    image_id: str,
    image_repo: Annotated[
        ImageRepositoryInterface, Depends(Provide[DependencyContainer.image_repo])
    ],
) -> StreamingResponse:
    try:
        image_uuid = uuid.UUID(image_id)
    except ValueError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=f"Invalid UUID: {image_id}"
        ) from None

    try:
        raw = image_repo.open_raw(image_uuid)
    except FileNotFoundError:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"Image {image_id} not found"
        ) from None

    return StreamingResponse(
        raw.iter_chunks(),
        media_type="application/octet-stream",
        headers={
            "x-image-shape": f"{raw.shape[0]},{raw.shape[1]}",
            "x-image-dtype": raw.dtype,
            "content-length": str(raw.length),
        },
    )
