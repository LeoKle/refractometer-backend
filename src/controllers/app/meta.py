from fastapi import APIRouter
from fastapi.responses import JSONResponse

from config import config

router = APIRouter()


@router.get("/version", response_class=JSONResponse)
def version():
    return {"version": config.VERSION}
