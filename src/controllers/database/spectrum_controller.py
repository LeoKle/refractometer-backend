from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from containers.container import DependencyContainer
from custom_types.spectrum import Spectrum
from interfaces.database.services.spectrum_service_interface import ISpectrumService

router = APIRouter()


@router.get("/spectrums")
@inject
def get_all_spectrums(
    spectrum_service: Annotated[
        ISpectrumService, Depends(Provide[DependencyContainer.spectrum_service])
    ],
):
    spectrums = spectrum_service.get_spectrums()
    return spectrums


@router.get("/spectrum/{spectrum_name}")
@inject
def get_spectrum(
    spectrum_name: str,
    spectrum_service: Annotated[
        ISpectrumService, Depends(Provide[DependencyContainer.spectrum_service])
    ],
):
    spectrum_data = spectrum_service.load_spectrum(spectrum_name)
    if spectrum_data:
        return spectrum_data
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spectrum not found")


@router.post("/spectrum")
@inject
def post_spectrum(
    spectrum_input: Spectrum,
    spectrum_service: Annotated[
        ISpectrumService, Depends(Provide[DependencyContainer.spectrum_service])
    ],
):
    spectrum_name = spectrum_input.name
    wavelengths = spectrum_input.wavelengths
    intensities = spectrum_input.intensities

    if not (spectrum_name and wavelengths and intensities):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request data")

    spectrum_service.save_spectrum(spectrum_name, wavelengths, intensities)

    return {"message": "Spectrum created successfully"}


@router.patch("/spectrum")
@inject
def patch_spectrum(
    spectrum_input: Spectrum,
    spectrum_service: Annotated[
        ISpectrumService, Depends(Provide[DependencyContainer.spectrum_service])
    ],
):
    spectrum_name = spectrum_input.name
    wavelengths = spectrum_input.wavelengths
    intensities = spectrum_input.intensities

    if not (spectrum_name and wavelengths and intensities):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request data")

    spectrum_service.update_spectrum(spectrum_name, wavelengths, intensities)
    return {"message": "Spectrum updated successfully"}


@router.delete("/spectrum/{spectrum_name}")
@inject
def delete_spectrum(
    spectrum_name: str,
    spectrum_service: Annotated[
        ISpectrumService, Depends(Provide[DependencyContainer.spectrum_service])
    ],
):
    if spectrum_service.delete_spectrum(spectrum_name):
        return {"message": "Spectrum deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spectrum does not exist")
