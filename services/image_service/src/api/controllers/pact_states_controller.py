import uuid
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request

from containers.container import DependencyContainer
from interfaces.image_repository_interface import ImageRepositoryInterface
from models.detector_image import DetectorImage

router = APIRouter(prefix="/_pact")

EXISTING_IMAGE_ID = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")


@router.post("/provider_states")
@inject
async def provider_states(
    request: Request,
    image_repo: Annotated[
        ImageRepositoryInterface, Depends(Provide[DependencyContainer.image_repo])
    ],
) -> dict[str, str]:
    body = await request.json()
    state = body.get("state", "")
    action = body.get("action", "setup")
    params = body.get("params") or {}

    if action == "setup" and state == "an image exists":
        image_id = uuid.UUID(params.get("id", str(EXISTING_IMAGE_ID)))
        try:
            image_repo.open_raw(image_id)
        except FileNotFoundError:
            image_repo.save_image(
                DetectorImage(id=image_id, values=[[0.1, 0.2], [0.3, 0.4]], shape=(2, 2))
            )

    # "no image exists" relies on the id never being created; the image service
    # has no delete, so there is nothing to tear down.
    return {"result": "ok"}
