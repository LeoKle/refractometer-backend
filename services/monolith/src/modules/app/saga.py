import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import partial

from loguru import logger


@dataclass(frozen=True)
class SagaStep[C]:
    name: str
    action: Callable[[C], None]
    compensation: Callable[[C, Exception], None] | None = None
    retries: int = 0  # forward recovery, only for transient errors
    pivot: bool = False  # once this step succeeds the saga only moves forward


class SagaAborted(Exception):
    """A step up to and including the pivot failed; attempted steps were compensated."""


class SagaIncomplete(Exception):
    """A step after the pivot failed even after retries; nothing was rolled back."""


class Saga[C]:
    def __init__(
        self,
        steps: list[SagaStep[C]],
        is_transient: Callable[[Exception], bool],
        backoff_seconds: float = 1.0,
        compensation_retries: int = 3,
    ):
        self.steps = steps
        self.is_transient = is_transient
        self.backoff_seconds = backoff_seconds
        self.compensation_retries = compensation_retries

    def run(self, ctx: C) -> None:
        attempted: list[SagaStep[C]] = []
        committed = False
        for step in self.steps:
            if not committed:
                attempted.append(step)  # outcome may be unknown -> compensate defensively
            try:
                self._with_retry(partial(step.action, ctx), step.retries)
            except Exception as err:
                if committed:
                    raise SagaIncomplete(step.name) from err
                self._compensate(reversed(attempted), ctx, err)
                raise SagaAborted(step.name) from err
            committed = committed or step.pivot

    def _with_retry(self, fn: Callable[[], None], retries: int) -> None:
        for attempt in range(retries + 1):
            try:
                fn()
            except Exception as err:
                if attempt == retries or not self.is_transient(err):
                    raise
                logger.warning(f"Transient error, retry {attempt + 1}/{retries}: {err}")
                time.sleep(self.backoff_seconds * 2**attempt)
            else:
                return

    def _compensate(self, steps: Iterable[SagaStep[C]], ctx: C, cause: Exception) -> None:
        for step in steps:
            if step.compensation is None:
                continue
            try:
                self._with_retry(partial(step.compensation, ctx, cause), self.compensation_retries)
            except Exception:  # noqa: BLE001 - best effort, keep compensating the rest
                logger.exception(f"Compensation of '{step.name}' failed; manual cleanup needed")
