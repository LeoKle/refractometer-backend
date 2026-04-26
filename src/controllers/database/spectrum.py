from fastapi import APIRouter, HTTPException, status

from custom_types.spectrum import Spectrum
from instance import refractometer_app_instance as app

router = APIRouter()


@router.get("/spectrums")
def get_all_spectrums():
    spectrums = app.database.spectrum_service().get_spectrums()
    return spectrums


@router.get("/spectrum/{spectrum_name}")
def get_spectrum(spectrum_name: str):
    spectrum_data = app.database.spectrum_service().load_spectrum(spectrum_name)
    if spectrum_data:
        return spectrum_data
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spectrum not found"
        )


@router.post("/spectrum")
def post_spectrum(spectrum_input: Spectrum):
    spectrum_name = spectrum_input.name
    wavelengths = spectrum_input.wavelengths
    intensities = spectrum_input.intensities

    if not (spectrum_name and wavelengths and intensities):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request data"
        )

    app.database.spectrum_service().save_spectrum(
        spectrum_name, wavelengths, intensities
    )

    return {"message": "Spectrum created successfully"}


@router.patch("/spectrum")
def patch_spectrum(spectrum_input: Spectrum):
    spectrum_name = spectrum_input.name
    wavelengths = spectrum_input.wavelengths
    intensities = spectrum_input.intensities

    if not (spectrum_name and wavelengths and intensities):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request data"
        )

    app.database.spectrum_service().update_spectrum(
        spectrum_name, wavelengths, intensities
    )
    return {"message": "Spectrum updated successfully"}


@router.delete("/spectrum/{spectrum_name}")
def delete_spectrum(spectrum_name: str):
    if app.database.spectrum_service().delete_spectrum(spectrum_name):
        return {"message": "Spectrum deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spectrum does not exist"
        )
