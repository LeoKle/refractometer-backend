from fastapi import APIRouter, HTTPException, status

from backend.src.custom_types.simulation_result import SimulationResult
from backend.src.instance import refractometer_app_instance as app

router = APIRouter()


@router.get("/results")
def get_results():
    results = app.database.simulation_result_service().get_results()
    return results


@router.get("/result/{result_id}")
def get_result(result_id: str):
    result = app.database.simulation_result_service().load_result(result_id)

    return result


@router.post("/result")
def post_result(result: SimulationResult):
    app.database.simulation_result_service().save_result(result)


@router.patch("/result")
def patch_result(result: SimulationResult):
    if not result.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing id"
        )

    app.database.simulation_result_service().update_result(result)


@router.delete("/result/{result_id}")
def delete_result(result_id: str):
    app.database.simulation_result_service().delete_result(result_id)
