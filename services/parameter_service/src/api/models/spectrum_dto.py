from pydantic import BaseModel, Field


class SpectrumDTO(BaseModel):
    name: str
    id: str | None = Field(default=None)
    wavelengths: list[float]
    intensities: list[float]
