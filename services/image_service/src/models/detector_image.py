import uuid

from pydantic import BaseModel, Field


class DetectorImage(BaseModel):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4)
    values: list[list[float]] = Field(
        ..., description="A 2D matrix representing the detector image"
    )
    shape: tuple[int, int] = Field((2560, 2440))
