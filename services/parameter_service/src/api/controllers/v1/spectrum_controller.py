import uuid
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from api.models.spectrum_dto import SpectrumDTO
from containers.container import DependencyContainer
from interfaces.services.spectrum_service_interface import SpectrumServiceInterface
from models.spectrum import Spectrum

router = APIRouter()


@router.get("/spectrums", response_model=list[SpectrumDTO])
@inject
def get_all_spectrums(
    spectrum_service: Annotated[
        SpectrumServiceInterface, Depends(Provide[DependencyContainer.spectrum_service])
    ],
):
    spectrums: list[Spectrum] = spectrum_service.get_spectrums()
    return [SpectrumDTO(**spectrum.model_dump()) for spectrum in spectrums]


@router.get("/spectrum/{spectrum_id}", response_model=SpectrumDTO)
@inject
def get_spectrum(
    spectrum_id: uuid.UUID,
    spectrum_service: Annotated[
        SpectrumServiceInterface, Depends(Provide[DependencyContainer.spectrum_service])
    ],
):
    spectrum = spectrum_service.get_spectrum(spectrum_id)
    if spectrum:
        return SpectrumDTO(**spectrum.model_dump())
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spectrum not found")


@router.post("/spectrum", status_code=status.HTTP_201_CREATED)
@inject
def post_spectrum(
    spectrum_input: SpectrumDTO,
    spectrum_service: Annotated[
        SpectrumServiceInterface, Depends(Provide[DependencyContainer.spectrum_service])
    ],
):
    spectrum = Spectrum(**spectrum_input.model_dump())
    spectrum_service.save_spectrum(spectrum)
    return {"message": "Spectrum created successfully"}


@router.patch("/spectrum", response_model=SpectrumDTO)
@inject
def patch_spectrum(
    spectrum_input: SpectrumDTO,
    spectrum_service: Annotated[
        SpectrumServiceInterface, Depends(Provide[DependencyContainer.spectrum_service])
    ],
):
    if not spectrum_input.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request data")

    spectrum = Spectrum(**spectrum_input.model_dump())
    updated = spectrum_service.update_spectrum(spectrum)
    return SpectrumDTO(**updated.model_dump())


@router.delete("/spectrum/{spectrum_id}", status_code=status.HTTP_200_OK)
@inject
def delete_spectrum(
    spectrum_id: uuid.UUID,
    spectrum_service: Annotated[
        SpectrumServiceInterface, Depends(Provide[DependencyContainer.spectrum_service])
    ],
):
    if spectrum_service.delete_spectrum(spectrum_id):
        return {"message": "Spectrum deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spectrum does not exist")
