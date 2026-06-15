from pydantic import BaseModel, Field


class DetectorImageDTO(BaseModel):
    values: list[list[float]] = Field(
        ..., description="A 2D matrix representing the detector image"
    )
    shape: tuple[int, int] = Field((2560, 2440))


class DetectorPostResult(BaseModel):
    id: str
