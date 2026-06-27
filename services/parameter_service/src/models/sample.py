import uuid

from pydantic import BaseModel, Field


class SellmeierCoefficients(BaseModel):
    B: list[float]
    C: list[float]


class Sample(BaseModel):
    name: str
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    sellmeier_coefficients: SellmeierCoefficients
