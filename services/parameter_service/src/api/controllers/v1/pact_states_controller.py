"""Provider states for the contract with refractometer-common-layer.

Only mounted when ENABLE_PACT_STATES is set. Every setup starts from an empty
store and seeds what the state asks for; teardown empties the store again.
"""

import uuid
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Request, status

from containers.container import DependencyContainer
from interfaces.services.sample_service_interface import ISampleService
from interfaces.services.spectrum_service_interface import SpectrumServiceInterface
from models.sample import Sample, SellmeierCoefficients
from models.spectrum import Spectrum

router = APIRouter(prefix="/_pact")

EXAMPLE_SAMPLE_ID = uuid.UUID("93162ee4-5716-4059-a8a8-fc02e125543f")
EXAMPLE_SPECTRUM_ID = uuid.UUID("4f8c2a1e-6b3d-4e7a-9c5f-2d1b8e3a7c90")

SAMPLE_STATES = {"samples exist", "a sample exists"}
SPECTRUM_STATES = {"spectrums exist", "a spectrum exists"}


def _example_sample(sample_id: uuid.UUID) -> Sample:
    return Sample(
        id=sample_id,
        name="Test Sample PACT",
        sellmeier_coefficients=SellmeierCoefficients(B=[1.0, 2.0, 3.0], C=[1.0, 2.0, 3.0]),
    )


def _example_spectrum(spectrum_id: uuid.UUID) -> Spectrum:
    return Spectrum(
        id=spectrum_id,
        name="Test Spectrum PACT",
        wavelengths=[400.0, 500.0, 600.0],
        intensities=[0.2, 0.9, 0.4],
    )


def _clear(sample_service: ISampleService, spectrum_service: SpectrumServiceInterface) -> None:
    for sample in sample_service.get_samples():
        sample_service.delete_sample(str(sample.id))
    for spectrum in spectrum_service.get_spectrums():
        spectrum_service.delete_spectrum(spectrum.id)


@router.post("/provider_states")
@inject
async def provider_states(
    request: Request,
    sample_service: Annotated[
        ISampleService,
        Depends(Provide[DependencyContainer.sample_service]),
    ],
    spectrum_service: Annotated[
        SpectrumServiceInterface,
        Depends(Provide[DependencyContainer.spectrum_service]),
    ],
) -> dict[str, str]:
    body = await request.json()
    state = body.get("state")
    action = body.get("action")
    params = body.get("params") or {}

    if action not in {"setup", "teardown"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing action")

    # "no sample exists", "no spectrum exists", "sample can be created" and
    # "spectrum can be created" only need the empty store.
    _clear(sample_service, spectrum_service)

    if action == "setup" and state in SAMPLE_STATES:
        sample_id = uuid.UUID(params.get("id", str(EXAMPLE_SAMPLE_ID)))
        sample_service.save_sample(_example_sample(sample_id))

    if action == "setup" and state in SPECTRUM_STATES:
        spectrum_id = uuid.UUID(params.get("id", str(EXAMPLE_SPECTRUM_ID)))
        spectrum_service.save_spectrum(_example_spectrum(spectrum_id))

    return {"result": "ok"}
