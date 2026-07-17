from datetime import datetime

import httpx
from loguru import logger
from pydantic import BaseModel, Field, ValidationError

from custom_types.simulation_queue import SimulationQueueElement
from interfaces.queue_service_interface import QueueServiceInterface


class QueueService(QueueServiceInterface):
    def __init__(self, base_url: str):
        self.base_url = base_url

    class SimulationQueueResponse(BaseModel):
        parameters: dict

        index: int | None = Field(default=None)
        being_processed: bool | None = Field(default=None)

        issuer: str | None = Field(default=None)
        callback_url: str | None = Field(default=None)
        id: str | None = Field(default=None)
        name: str | None = Field(default=None)
        image_id: str | None = Field(default=None)
        issued_at: datetime
        completed_at: datetime | None = Field(default=None)

    def claim_element(self):
        response = httpx.get(self.base_url + "/api/queue/claim")

        if response.status_code != 200:
            return None

        data = self.SimulationQueueResponse(**response.json())

        try:
            queue_element = SimulationQueueElement(**data.model_dump())
        except ValidationError as ex:
            logger.error(ex)
            return None
        else:
            return queue_element

    def delete_queued_element(self, queue_id: str):
        response = httpx.delete(self.base_url + f"/api/queue/{queue_id}")

        return response.status_code == 204
