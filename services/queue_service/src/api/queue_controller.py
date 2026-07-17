from datetime import UTC, datetime
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from api.queue_requests import SimulationQueueRequest
from api.queue_responses import SimulationQueueResponse
from container import DependencyContainer
from interfaces.queue_service_interface import QueueServiceInterface
from models.queue_element import QueueElement

router = APIRouter(prefix="/api")


def to_response(element: QueueElement) -> SimulationQueueResponse:
    return SimulationQueueResponse(
        parameters=element.parameters,
        index=element.index,
        being_processed=element.being_processed,
        issuer=element.issuer,
        callback_url=element.callback_url,
        id=str(element.id),
        name=element.name,
        image_id=element.image_id,
        issued_at=element.issued_at,
        completed_at=element.completed_at,
    )


@router.get("/queue/claim", response_model=SimulationQueueResponse)
@inject
def claim_element(
    queue_service: Annotated[
        QueueServiceInterface,
        Depends(Provide[DependencyContainer.queue_service]),
    ],
):
    element = queue_service.claim_next_simulation()

    if element is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No queued simulations available",
        )

    return to_response(element)


@router.get("/queued", response_model=list[SimulationQueueResponse])
@inject
def get_results(
    queue_service: Annotated[
        QueueServiceInterface,
        Depends(Provide[DependencyContainer.queue_service]),
    ],
):
    results = queue_service.get_queued_simulations()
    return [to_response(result) for result in results]


@router.get("/queue/{queued_element_id}", response_model=SimulationQueueResponse)
@inject
def get_result(
    queued_element_id: str,
    queue_service: Annotated[
        QueueServiceInterface,
        Depends(Provide[DependencyContainer.queue_service]),
    ],
):
    result = queue_service.load_queued_simulation(queued_element_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Queue element '{queued_element_id}' not found",
        )

    return to_response(result)


@router.post("/queue", status_code=status.HTTP_201_CREATED)
@inject
def post_result(
    element_to_queue: SimulationQueueRequest,
    queue_service: Annotated[
        QueueServiceInterface,
        Depends(Provide[DependencyContainer.queue_service]),
    ],
):
    queue_element = QueueElement(
        parameters=element_to_queue.parameters,
        issuer=element_to_queue.issuer,
        callback_url=element_to_queue.callback_url,
        name=element_to_queue.name,
        issued_at=datetime.now(UTC),
    )

    queue_service.save_queued_simulation(queue_element)

    return {"id": str(queue_element.id)}


@router.patch("/queue/{queued_element_id}", response_model=SimulationQueueResponse)
@inject
def patch_result(
    queued_element_id: str,
    queued_element: SimulationQueueRequest,
    queue_service: Annotated[
        QueueServiceInterface,
        Depends(Provide[DependencyContainer.queue_service]),
    ],
):
    existing = queue_service.load_queued_simulation(queued_element_id)

    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Queue element '{queued_element_id}' not found",
        )

    existing.parameters = queued_element.parameters
    existing.issuer = queued_element.issuer
    existing.callback_url = queued_element.callback_url
    existing.name = queued_element.name

    queue_service.update_queued_simulation(existing)

    return to_response(existing)


@router.delete("/queue/{queued_element_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_result(
    queued_element_id: str,
    queue_service: Annotated[
        QueueServiceInterface,
        Depends(Provide[DependencyContainer.queue_service]),
    ],
):
    existing = queue_service.load_queued_simulation(queued_element_id)

    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Queue element '{queued_element_id}' not found",
        )

    queue_service.delete_queued_simulation(queued_element_id)
