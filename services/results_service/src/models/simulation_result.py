import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SimulationResult(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    parameters: dict
    image_id: str | None = Field(default=None)
    issued_at: datetime
    completed_at: datetime
