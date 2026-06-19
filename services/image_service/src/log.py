import sys

from loguru import logger

from api.correlation import correlation_id


def patch_record(record):
    record["extra"]["correlation_id"] = correlation_id.get() or "-"
    record["extra"]["service"] = "image-service"


def setup_logging():
    logger.remove()

    logger.configure(patcher=patch_record)

    logger.add(
        sys.stdout,
        serialize=True,  # JSON logs
        diagnose=False,
    )
