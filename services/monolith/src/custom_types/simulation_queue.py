from pydantic import Field

from custom_types.simulation_result import SimulationResult


class SimulationQueueElement(SimulationResult):
    index: int | None = Field(default=None)
    being_processed: bool | None = False
    issuer: str | None = Field(default=None)
    callback_url: str | None = Field(default=None)
