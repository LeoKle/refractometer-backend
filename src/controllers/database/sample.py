from fastapi import APIRouter, HTTPException, status

from backend.src.custom_types.sample import Sample
from backend.src.instance import refractometer_app_instance as app

router = APIRouter()


@router.get("/samples")
def get_all_samples():
    samples = app.database.sample_service().get_samples()
    return samples


@router.get("/sample/{sample_id}")
def get_sample(sample_id: str):
    sample = app.database.sample_service().load_sample(sample_id)
    return sample


@router.post("/sample")
def post_sample(sample_input: Sample):
    app.database.sample_service().save_sample(sample_input)


@router.patch("/sample")
def patch_sample(sample_input: Sample):
    if not sample_input.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing id"
        )

    app.database.sample_service().update_sample(sample_input)


@router.delete("/sample/{sample_id}")
def delete_sample(sample_id: str):
    app.database.sample_service().delete_sample(sample_id)
