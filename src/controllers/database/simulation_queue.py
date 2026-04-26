from fastapi import APIRouter, HTTPException, status

from custom_types.simulation_queue import SimulationQueueElement
from instance import refractometer_app_instance as app

router = APIRouter()


@router.get("/queued")
def get_results():
    results = app.database.simulation_queue_service().get_queued_simulations()
    return results


@router.get("/queue/{queued_element_id}")
def get_result(queued_element_id: str):
    result = app.database.simulation_queue_service().load_queued_simulation(
        queued_element_id
    )

    return result


@router.post("/queue")
def post_result(element_to_queue: SimulationQueueElement):
    app.database.simulation_queue_service().save_queued_simulation(element_to_queue)


@router.patch("/queue")
def patch_result(queued_element: SimulationQueueElement):
    if not queued_element.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing id"
        )

    app.database.simulation_queue_service().update_queued_simulation(queued_element)


@router.delete("/queue/{queued_element_id}")
def delete_result(queued_element_id: str):
    app.database.simulation_queue_service().delete_queued_simulation(queued_element_id)
