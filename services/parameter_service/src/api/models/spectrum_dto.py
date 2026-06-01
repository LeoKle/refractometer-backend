import uuid

from pydantic import BaseModel, Field


class SpectrumDTO(BaseModel):
    name: str
    id: uuid.UUID | None = Field(default=None)
    wavelengths: list[float]
    intensities: list[float]
