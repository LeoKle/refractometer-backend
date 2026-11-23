import threading
import time
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime

from loguru import logger
from refractometer_common.image import (
    CreateImageRequest,
    ImageClientConnectionException,
    ImageClientInterface,
    ImageNotFoundException,
)
from refractometer_common.queue import (
    QueueClientConnectionException,
    QueueClientElementNotFoundException,
    QueueClientException,
    QueueClientInterface,
    SimulationQueueElement,
)
from refractometer_common.result import (
    SimulationResultClientConnectionException,
    SimulationResultClientInterface,
)

from custom_types.detector_image import DetectorImage
from interfaces.app.simulation_handler import SimulationHandlerInterface
from interfaces.app.simulation_interface import ISimulation
from modules.app.saga import Saga, SagaAborted, SagaIncomplete, SagaStep

TRANSIENT_ERRORS = (
    ImageClientConnectionException,  # includes timeouts
    QueueClientConnectionException,
    SimulationResultClientConnectionException,
)


def is_transient(err: Exception) -> bool:
    """Connection problems, timeouts and 5xx answers are worth retrying, everything else is not."""
    status = getattr(err, "status_code", None)
    return isinstance(err, TRANSIENT_ERRORS) or (status is not None and status >= 500)


@dataclass
class SimulationSagaContext:
    element: SimulationQueueElement
    detector_image: DetectorImage | None = None
    image_id: str | None = None
    result_id: str | None = None


class SimulationHandler(SimulationHandlerInterface):
    def __init__(
        self,
        simulation: ISimulation,
        queue_client: QueueClientInterface,
        image_service: ImageClientInterface,
        simulation_result_client: SimulationResultClientInterface,
        retries: int = 3,
        backoff_seconds: float = 1.0,
        idle_seconds: float = 5.0,
    ):
        self.simulation = simulation
        self.queue_client = queue_client
        self.image_service = image_service
        self.simulation_result_client = simulation_result_client
        self.retries = retries
        self.backoff_seconds = backoff_seconds
        self.idle_seconds = idle_seconds

        self.is_running = False
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return

        self.is_running = True
        self.thread = threading.Thread(target=self.process_queue, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()

    def process_queue(self):
        while self.is_running:
            try:
                element = self.queue_client.claim_element()
            except QueueClientElementNotFoundException:
                logger.info("No simulation queued, sleeping...")
                time.sleep(self.idle_seconds)
                continue
            except QueueClientException:
                logger.exception("Failed to claim queue element")
                time.sleep(self.idle_seconds)
                continue

            self.run_saga(element)

    def run_saga(self, element: SimulationQueueElement) -> None:
        logger.info(f"Processing simulation {element.id} (attempt {element.attempts})")
        try:
            saga = Saga(self._steps(), is_transient, backoff_seconds=self.backoff_seconds)
            saga.run(SimulationSagaContext(element))
        except SagaAborted as err:
            logger.warning(
                f"Simulation {element.id} rolled back at step '{err}': {err.__cause__!r}"
            )
        except SagaIncomplete as err:
            logger.error(
                f"Simulation {element.id} stored, but step '{err}' failed: {err.__cause__!r}. "
                "Re-running it is safe."
            )
        except Exception:  # noqa: BLE001 - never kill the worker
            logger.exception(f"Unexpected error in simulation {element.id}")
        else:
            logger.info(f"Simulation {element.id} completed")

    def _steps(self) -> list[SagaStep[SimulationSagaContext]]:
        return [
            # the claim already happened in process_queue, listed here so its compensation runs
            SagaStep("claim", self._noop, compensation=self._release),
            SagaStep("simulate", self._simulate),
            SagaStep(
                "upload_image",
                self._upload_image,
                compensation=self._delete_image,
                retries=self.retries,
            ),
            SagaStep(
                "create_result",
                self._create_result,
                compensation=self._delete_result,
                retries=self.retries,
                pivot=True,
            ),
            SagaStep("dequeue", self._dequeue, retries=self.retries),
            SagaStep("callback", self._callback),
        ]

    # actions

    @staticmethod
    def _noop(ctx: SimulationSagaContext) -> None:
        pass

    def _simulate(self, ctx: SimulationSagaContext) -> None:
        self.simulation.set_parameters(ctx.element.parameters)
        self.simulation.simulate()
        ctx.detector_image = self.simulation.get_detector_image()

    def _upload_image(self, ctx: SimulationSagaContext) -> None:
        request = CreateImageRequest(
            values=ctx.detector_image.values, shape=ctx.detector_image.shape
        )
        ctx.image_id = self.image_service.create_image(
            request, idempotency_key=f"{ctx.element.id}:upload_image"
        )

    def _create_result(self, ctx: SimulationSagaContext) -> None:
        result = self.simulation_result_client.create_result(
            ctx.element.parameters,
            ctx.image_id,
            ctx.element.issued_at,
            completed_at=datetime.now(UTC),
            idempotency_key=f"{ctx.element.id}:create_result",
        )
        ctx.result_id = str(result.id)

    def _dequeue(self, ctx: SimulationSagaContext) -> None:
        with suppress(QueueClientElementNotFoundException):  # already gone = done
            self.queue_client.delete_queued_element(ctx.element.id)

    def _callback(self, ctx: SimulationSagaContext) -> None:
        if ctx.element.callback_url:
            logger.info("Callback to invoke found")  # placeholder, unchanged

    # compensations (all idempotent)

    def _release(self, ctx: SimulationSagaContext, cause: Exception) -> None:
        with suppress(QueueClientElementNotFoundException):  # element deleted meanwhile
            self.queue_client.release_element(ctx.element.id, error=repr(cause))

    def _delete_image(self, ctx: SimulationSagaContext, cause: Exception) -> None:
        if ctx.image_id is None:
            logger.warning(
                f"Image id unknown, possible orphan for key {ctx.element.id}:upload_image"
            )
            return
        with suppress(ImageNotFoundException):
            self.image_service.delete_image(ctx.image_id)

    def _delete_result(self, ctx: SimulationSagaContext, cause: Exception) -> None:
        if ctx.result_id is None:
            if not is_transient(cause):
                return  # the service rejected the request, so nothing was stored
            # outcome unknown (response lost): replaying the same key returns the stored
            # result, or stores one that is deleted right away. Without this, a retry of
            # the element would get back a stale result pointing at the deleted image.
            self._create_result(ctx)
        self.simulation_result_client.delete_result(ctx.result_id)
