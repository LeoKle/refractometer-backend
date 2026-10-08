from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from api.controllers.v1.simulation_dtos import (
    CreateSimulationResultRequest,
    PatchSimulationResultRequest,
    SimulationResultResponse,
)
from containers.container import DependencyContainer
from interfaces.simulation_repository_interface import SimulationResultRepositoryInterface
from models.simulation_result import SimulationResult

router = APIRouter()


@router.get("/results")
@inject
def get_results(
    sim_result_repository: Annotated[
        SimulationResultRepositoryInterface,
        Depends(Provide[DependencyContainer.sim_result_repository]),
    ],
):
    results = sim_result_repository.get_results()

    return [SimulationResultResponse(**result.model_dump()) for result in results]


@router.get("/result/{result_id}")
@inject
def get_result(
    result_id: str,
    sim_result_repository: Annotated[
        SimulationResultRepositoryInterface,
        Depends(Provide[DependencyContainer.sim_result_repository]),
    ],
):
    result = sim_result_repository.load_result(result_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation result not found",
        )

    return SimulationResultResponse(**result.model_dump())


@router.post("/result")
@inject
def post_result(
    result_dto: CreateSimulationResultRequest,
    sim_result_repository: Annotated[
        SimulationResultRepositoryInterface,
        Depends(Provide[DependencyContainer.sim_result_repository]),
    ],
):
    result = SimulationResult(**result_dto.model_dump())

    saved_result = sim_result_repository.save_result(result)

    return SimulationResultResponse(**saved_result.model_dump())


@router.patch("/result")
@inject
def patch_result(
    result_dto: PatchSimulationResultRequest,
    sim_result_repository: Annotated[
        SimulationResultRepositoryInterface,
        Depends(Provide[DependencyContainer.sim_result_repository]),
    ],
):
    existing_result = sim_result_repository.load_result(result_dto.id)

    if not existing_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation result not found",
        )

    result = SimulationResult(**result_dto.model_dump())

    patched_result = sim_result_repository.update_result(result)

    return SimulationResultResponse(**patched_result.model_dump())


@router.delete("/result/{result_id}")
@inject
def delete_result(
    result_id: str,
    sim_result_repository: Annotated[
        SimulationResultRepositoryInterface,
        Depends(Provide[DependencyContainer.sim_result_repository]),
    ],
):
    sim_result_repository.delete_result(result_id)
