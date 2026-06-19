import uuid
from contextvars import ContextVar

correlation_id: ContextVar[str | None] = ContextVar(
    "correlation_id",
    default=None,
)


def get_or_create_correlation_id() -> str:
    cid = correlation_id.get()
    if cid:
        return cid

    cid = str(uuid.uuid4())
    correlation_id.set(cid)
    return cid
