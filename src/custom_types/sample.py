from typing import List, Optional
from pydantic import BaseModel, Field


class SellmeierCoefficients(BaseModel):
    B: List[float]
    C: List[float]


class Sample(BaseModel):
    name: str
    id: Optional[str] = Field(default=None)
    sellmeier_coefficients: SellmeierCoefficients
