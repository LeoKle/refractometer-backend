from datetime import datetime

from pydantic import BaseModel, Field

from custom_types.simulation_parameters import SimulationParameters


class SimulationResult(BaseModel):
    id: str | None = Field(default=None)
    name: str | None = Field(default=None)
    parameters: SimulationParameters
    image_id: str = Field(default=None)
    issued_at: datetime
    completed_at: datetime | None = Field(default=None)
