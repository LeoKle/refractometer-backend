from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from containers.container import DependencyContainer
from custom_types.simulation_queue import SimulationQueueElement
from interfaces.database.services.simulation_queue_service_interface import (
    ISimulationQueueService,
)

router = APIRouter()


@router.get("/queued")
@inject
def get_results(
    queue_service: Annotated[
        ISimulationQueueService, Depends(Provide[DependencyContainer.sim_queue_service])
    ],
):
    results = queue_service.get_queued_simulations()
    return results


@router.get("/queue/{queued_element_id}")
@inject
def get_result(
    queued_element_id: str,
    queue_service: Annotated[
        ISimulationQueueService, Depends(Provide[DependencyContainer.sim_queue_service])
    ],
):
    result = queue_service.load_queued_simulation(queued_element_id)

    return result


@router.post("/queue")
@inject
def post_result(
    element_to_queue: SimulationQueueElement,
    queue_service: Annotated[
        ISimulationQueueService, Depends(Provide[DependencyContainer.sim_queue_service])
    ],
):
    queue_service.save_queued_simulation(element_to_queue)


@router.patch("/queue")
@inject
def patch_result(
    queued_element: SimulationQueueElement,
    queue_service: Annotated[
        ISimulationQueueService, Depends(Provide[DependencyContainer.sim_queue_service])
    ],
):
    if not queued_element.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing id")

    queue_service.update_queued_simulation(queued_element)


@router.delete("/queue/{queued_element_id}")
@inject
def delete_result(
    queued_element_id: str,
    queue_service: Annotated[
        ISimulationQueueService, Depends(Provide[DependencyContainer.sim_queue_service])
    ],
):
    queue_service.delete_queued_simulation(queued_element_id)
