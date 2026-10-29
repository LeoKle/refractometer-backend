import uuid

import numpy as np
from gridfs import GridFS
from pymongo.database import Database

from interfaces.image_repository_interface import ImageRepositoryInterface
from models.detector_image import DetectorImage
from models.raw_image import RawImage

ALLOWED_DTYPES = {"float32", "float64", "uint8", "uint16", "int16", "int32"}


class ImageRepository(ImageRepositoryInterface):
    def __init__(self, db: Database):
        self.fs = GridFS(db)

    def save_raw(self, image_id, data, shape, dtype):
        if dtype not in ALLOWED_DTYPES:
            msg = f"Unsupported dtype: {dtype}"
            raise ValueError(msg)
        dt = np.dtype(dtype)
        expected = shape[0] * shape[1] * dt.itemsize
        if len(data) != expected:
            msg = f"Expected {expected} bytes for shape {shape} and dtype {dtype}, got {len(data)}"
            raise ValueError(msg)
        metadata = {"uuid": str(image_id), "shape": list(shape), "dtype": str(dt)}
        self.fs.put(data, metadata=metadata, filename=str(image_id))

    def open_raw(self, image_id: uuid.UUID) -> RawImage:
        grid_out = self.fs.find_one({"metadata.uuid": str(image_id)})
        if grid_out is None:
            msg = f"Image with id {image_id} not found"
            raise FileNotFoundError(msg)
        return RawImage(
            stream=grid_out,
            shape=tuple(grid_out.metadata["shape"]),
            dtype=grid_out.metadata["dtype"],
            length=grid_out.length,
        )

    def save_image(self, detector_image: DetectorImage) -> None:
        matrix = np.asarray(detector_image.values, dtype=np.float64).reshape(detector_image.shape)
        self.save_raw(detector_image.id, matrix.tobytes(), tuple(matrix.shape), "float64")

    def get_image(self, id: uuid.UUID) -> DetectorImage:
        raw = self.open_raw(id)
        data = b"".join(raw.iter_chunks())
        matrix = np.frombuffer(data, dtype=raw.dtype).reshape(raw.shape)
        return DetectorImage(id=id, values=matrix.tolist(), shape=raw.shape)
