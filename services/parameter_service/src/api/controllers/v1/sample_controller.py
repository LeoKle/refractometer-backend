from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from api.models.sample_dto import SampleDTO
from containers.container import DependencyContainer
from interfaces.services.sample_service_interface import ISampleService

router = APIRouter()


@router.get("/samples")
@inject
def get_all_samples(
    sample_service: Annotated[ISampleService, Depends(Provide[DependencyContainer.sample_service])],
):
    samples = sample_service.get_samples()
    return samples


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


@router.post("/sample")
@inject
def post_sample(
    sample_input: SampleDTO,
    sample_service: Annotated[ISampleService, Depends(Provide[DependencyContainer.sample_service])],
):
    sample_service.save_sample(sample_input)


@router.patch("/sample")
@inject
def patch_sample(
    sample_input: SampleDTO,
    sample_service: Annotated[ISampleService, Depends(Provide[DependencyContainer.sample_service])],
):
    if not sample_input.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing id")

    sample_service.update_sample(sample_input)


@router.delete("/sample/{sample_id}")
@inject
def delete_sample(
    sample_id: str,
    sample_service: Annotated[ISampleService, Depends(Provide[DependencyContainer.sample_service])],
):
    sample_service.delete_sample(sample_id)
