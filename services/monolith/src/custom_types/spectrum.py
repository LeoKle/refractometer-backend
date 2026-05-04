from pydantic import BaseModel, Field


class Spectrum(BaseModel):
    name: str
    id: str | None = Field(default=None)
    wavelengths: list[float]
    intensities: list[float]
