from fastapi import APIRouter

from backend.src.custom_types.detector_image import DetectorImage
from backend.src.instance import refractometer_app_instance as app

router = APIRouter()


@router.get("/image/{image_id}")
def get_result(image_id: str) -> DetectorImage:
    result = app.database.image_service().retrieve_image(image_id)

    return result
