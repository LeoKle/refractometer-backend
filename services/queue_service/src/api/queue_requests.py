from pydantic import BaseModel, Field


class SimulationQueueRequest(BaseModel):
    parameters: dict

    issuer: str | None = Field(default=None)
    callback_url: str | None = Field(default=None)
    name: str | None = Field(default=None)
