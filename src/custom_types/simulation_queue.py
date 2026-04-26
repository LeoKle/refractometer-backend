from typing import Optional

from pydantic import Field
from custom_types.simulation_result import SimulationResult


class SimulationQueueElement(SimulationResult):
    index: Optional[int] = Field(default=None)
    being_processed: Optional[bool] = Field(default=None)
    issuer: Optional[str] = Field(default=None)
    callback_url: Optional[str] = Field(default=None)
