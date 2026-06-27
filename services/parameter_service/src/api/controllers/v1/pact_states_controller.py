import uuid
from typing import Annotated, Literal

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request

from api.models.sample_dto import SampleDTO, SellmeierCoefficientsDTO
from containers.container import DependencyContainer
from interfaces.services.sample_service_interface import ISampleService

router = APIRouter(prefix="/_pact")

EXAMPLE_SAMPLE_ID = uuid.UUID("93162ee4-5716-4059-a8a8-fc02e125543f")


@router.post("/provider_states")
@inject
async def provider_states(
    request: Request,
    sample_service: Annotated[
        ISampleService,
        Depends(Provide[DependencyContainer.sample_service]),
    ],
) -> dict[str, str]:
    body = await request.json()

    state = body.get("state")
    action = body.get("action", "setup")

    if action == "teardown":
        if state in {"sample exists", "sample exists with id sample-1"}:
            sample_service.delete_sample(EXAMPLE_SAMPLE_ID)

        return {"result": "cleaned"}

    if state == "sample exists" or state == "sample exists with id sample-1":
        sample_service.save_sample(
            SampleDTO(
                id=EXAMPLE_SAMPLE_ID,
                name="Test Sample",
                sellmeier_coefficients=SellmeierCoefficientsDTO(
                    B=[1.0, 2.0, 3.0],
                    C=[1.0, 2.0, 3.0],
                ),
            )
        )

    elif state == "sample does not exist":
        # ensure clean state
        sample_service.delete_sample(EXAMPLE_SAMPLE_ID)

    elif state == "sample can be created":
        # nothing needed, just ensure clean DB
        sample_service.delete_sample(EXAMPLE_SAMPLE_ID)

    return {"result": "ok"}
