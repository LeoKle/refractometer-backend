import re
import uuid
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request

from containers.container import DependencyContainer
from interfaces.image_repository_interface import ImageRepositoryInterface
from models.detector_image import DetectorImage

router = APIRouter(prefix="/_pact")

EXISTING_IMAGE_ID = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")

# Pact V2 files carry the id in the state name ("an image with ID <uuid> exists"),
# V3+ files pass it as a param ({"name": "an image exists", "params": {"id": ...}}).
_IMAGE_EXISTS = re.compile(r"^an image( with ID (?P<id>[0-9a-fA-F-]{36}))? exists$")
_NO_IMAGE_EXISTS = re.compile(r"^no image exists( with ID (?P<id>[0-9a-fA-F-]{36}))?$")


def _image_id(match: re.Match, params: dict) -> uuid.UUID | None:
    raw = params.get("id") or match.group("id")
    return uuid.UUID(raw) if raw else None


def _ensure_exists(image_repo: ImageRepositoryInterface, image_id: uuid.UUID) -> None:
    try:
        image_repo.open_raw(image_id)
    except FileNotFoundError:
        image_repo.save_image(
            DetectorImage(id=image_id, values=[[0.1, 0.2], [0.3, 0.4]], shape=(2, 2))
        )


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

    # Every state is set up explicitly and torn down again, so interactions do not
    # depend on the order the verifier runs them in or on data left in the database.
    if match := _IMAGE_EXISTS.match(state):
        image_id = _image_id(match, params) or EXISTING_IMAGE_ID
        if action == "setup":
            _ensure_exists(image_repo, image_id)
        else:
            image_repo.delete_image(image_id)
    elif (match := _NO_IMAGE_EXISTS.match(state)) and action == "setup":
        image_id = _image_id(match, params)
        if image_id is not None:
            image_repo.delete_image(image_id)

    return {"result": "ok"}
