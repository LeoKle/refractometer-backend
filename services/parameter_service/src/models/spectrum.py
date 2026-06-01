import uuid

from pydantic import BaseModel, Field


class Spectrum(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    wavelengths: list[float]
    intensities: list[float]
