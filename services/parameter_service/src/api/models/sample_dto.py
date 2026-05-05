from pydantic import BaseModel, Field


class SellmeierCoefficientsDTO(BaseModel):
    B: list[float]
    C: list[float]


class SampleDTO(BaseModel):
    name: str
    id: str | None = Field(default=None)
    sellmeier_coefficients: SellmeierCoefficientsDTO
