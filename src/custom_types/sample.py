from pydantic import BaseModel, Field


class SellmeierCoefficients(BaseModel):
    B: list[float]
    C: list[float]


class Sample(BaseModel):
    name: str
    id: str | None = Field(default=None)
    sellmeier_coefficients: SellmeierCoefficients
