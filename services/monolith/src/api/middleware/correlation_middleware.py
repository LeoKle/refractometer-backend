import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from api.correlation import correlation_id


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """assigns correlation ids to requests if not already set
    available to downstream services via ```correlation_id.get()```"""

    async def dispatch(self, request: Request, call_next):
        cid = request.headers.get("X-Correlation-ID")

        if not cid:
            cid = str(uuid.uuid4())

        token = correlation_id.set(cid)

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = cid
            return response
        finally:
            correlation_id.reset(token)
