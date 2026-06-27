import uuid
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Request, status

from containers.container import DependencyContainer
from interfaces.services.sample_service_interface import ISampleService
from models.sample import Sample, SellmeierCoefficients

router = APIRouter(prefix="/_pact")

EXAMPLE_SAMPLE_ID = uuid.UUID("93162ee4-5716-4059-a8a8-fc02e125543f")
SAMPLE_REQUIRING_STATES = {
    "samples exist",
    "sample exists with id 93162ee4-5716-4059-a8a8-fc02e125543f",
}


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
    action = body.get("action")

    if not action:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing action")

    if (
        action == "setup"
        and state in SAMPLE_REQUIRING_STATES
        and sample_service.load_sample(str(EXAMPLE_SAMPLE_ID)) is None
    ):
        sample_service.save_sample(
            Sample(
                id=EXAMPLE_SAMPLE_ID,
                name="Test Sample PACT",
                sellmeier_coefficients=SellmeierCoefficients(
                    B=[1.0, 2.0, 3.0],
                    C=[1.0, 2.0, 3.0],
                ),
            )
        )
    # "sample can be created" and "no samples exist" require a clean db — teardown handles that

    if action == "teardown":
        for sample in sample_service.get_samples():
            sample_service.delete_sample(str(sample.id))

    return {"result": "ok"}
