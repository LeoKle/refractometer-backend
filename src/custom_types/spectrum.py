from typing import List, Optional
from pydantic import BaseModel, Field


class Spectrum(BaseModel):
    name: str
    id: Optional[str] = Field(default=None)
    wavelengths: List[float]
    intensities: List[float]
