from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from custom_types.simulation_parameters import SimulationParameters


class SimulationResult(BaseModel):
    id: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    parameters: SimulationParameters
    image_id: str = Field(default=None)
    issued_at: datetime
    completed_at: Optional[datetime] = Field(default=None)
