from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from containers.container import DependencyContainer
from custom_types.simulation_result import SimulationResult
from interfaces.database.services.simulation_result_service_interface import (
    ISimulationResultService,
)

router = APIRouter()


@router.get("/results")
@inject
def get_results(
    sim_result_service: Annotated[
        ISimulationResultService,
        Depends(Provide[DependencyContainer.sim_results_service]),
    ],
):
    results = sim_result_service.get_results()
    return results


@router.get("/result/{result_id}")
@inject
def get_result(
    result_id: str,
    sim_result_service: Annotated[
        ISimulationResultService,
        Depends(Provide[DependencyContainer.sim_results_service]),
    ],
):
    result = sim_result_service.load_result(result_id)

    return result


@router.post("/result")
@inject
def post_result(
    result: SimulationResult,
    sim_result_service: Annotated[
        ISimulationResultService,
        Depends(Provide[DependencyContainer.sim_results_service]),
    ],
):
    sim_result_service.save_result(result)


@router.patch(
    "/result",
)
@inject
def patch_result(
    result: SimulationResult,
    sim_result_service: Annotated[
        ISimulationResultService,
        Depends(Provide[DependencyContainer.sim_results_service]),
    ],
):
    if not result.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing id"
        )

    sim_result_service.update_result(result)


@router.delete("/result/{result_id}")
@inject
def delete_result(
    result_id: str,
    sim_result_service: Annotated[
        ISimulationResultService,
        Depends(Provide[DependencyContainer.sim_results_service]),
    ],
):
    sim_result_service.delete_result(result_id)
