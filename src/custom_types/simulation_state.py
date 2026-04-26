from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel


class SimulationState(BaseModel):
    severity: Optional[
        Literal["danger", "success", "warning", "secondary", "info", "help"]
    ] = None
    text: str


class SimulationStates(Enum):
    IDLE = SimulationState(severity="success", text="Idle")
    SETTING_UP = SimulationState(severity="warning", text="Setting up")
    SET_UP = SimulationState(severity="warning", text="Set up")
    SIMULATING = SimulationState(severity="warning", text="Simulating")
    DETECTOR_SIMULATION = SimulationState(
        severity="warning", text="Generating Detector Image"
    )
    SIMULATION_DONE = SimulationState(
        severity="success", text="Generated Detectorimage"
    )
