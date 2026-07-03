import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class QueueElement(BaseModel):
    parameters: dict
    id: uuid.UUID = Field(default_factory=uuid.uuid4)

    index: int | None = Field(default=None)
    being_processed: bool = False

    issuer: str | None = Field(default=None)
    callback_url: str | None = Field(default=None)
    name: str | None = Field(default=None)
    image_id: str = Field(default=None)
    issued_at: datetime
    completed_at: datetime | None = Field(default=None)
