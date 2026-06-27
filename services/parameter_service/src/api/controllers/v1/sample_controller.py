import uuid
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from api.models.sample_dto import SampleDTO
from containers.container import DependencyContainer
from interfaces.services.sample_service_interface import ISampleService
from models.sample import Sample, SellmeierCoefficients

router = APIRouter()


def _dto_to_domain(sample_input: SampleDTO) -> Sample:
    return Sample(
        id=uuid.UUID(sample_input.id) if sample_input.id else uuid.uuid4(),
        name=sample_input.name,
        sellmeier_coefficients=SellmeierCoefficients(
            B=sample_input.sellmeier_coefficients.B,
            C=sample_input.sellmeier_coefficients.C,
        ),
    )


@router.get("/samples")
@inject
def get_all_samples(
    sample_service: Annotated[ISampleService, Depends(Provide[DependencyContainer.sample_service])],
):
    return sample_service.get_samples()


@router.get("/sample/{sample_id}")
@inject
def get_sample(
    sample_id: str,
    sample_service: Annotated[ISampleService, Depends(Provide[DependencyContainer.sample_service])],
):
    sample = sample_service.load_sample(sample_id)
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return sample


@router.post("/sample", status_code=status.HTTP_200_OK)
@inject
def post_sample(
    sample_input: SampleDTO,
    sample_service: Annotated[ISampleService, Depends(Provide[DependencyContainer.sample_service])],
):
    sample_service.save_sample(_dto_to_domain(sample_input))


@router.patch("/sample", status_code=status.HTTP_200_OK)
@inject
def patch_sample(
    sample_input: SampleDTO,
    sample_service: Annotated[ISampleService, Depends(Provide[DependencyContainer.sample_service])],
):
    if not sample_input.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing id")
    sample_service.update_sample(_dto_to_domain(sample_input))


@router.delete("/sample/{sample_id}", status_code=status.HTTP_200_OK)
@inject
def delete_sample(
    sample_id: str,
    sample_service: Annotated[ISampleService, Depends(Provide[DependencyContainer.sample_service])],
):
    sample_service.delete_sample(sample_id)
