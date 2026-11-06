import uuid

import numpy as np
from bson import ObjectId
from gridfs import GridFS
from gridfs.errors import FileExists
from pymongo.database import Database

from interfaces.image_repository_interface import ImageRepositoryInterface
from models.detector_image import DetectorImage
from models.raw_image import RawImage

ALLOWED_DTYPES = {"float32", "float64", "uint8", "uint16", "int16", "int32"}

IDEMPOTENCY_FIELD = "metadata.idempotency_key"


class ImageRepository(ImageRepositoryInterface):
    def __init__(self, db: Database, bucket: str = "fs"):
        self.fs = GridFS(db, collection=bucket)
        self._files = db[f"{bucket}.files"]
        self._files.create_index(
            IDEMPOTENCY_FIELD,
            name="uniq_idempotency_key",
            unique=True,
            partialFilterExpression={IDEMPOTENCY_FIELD: {"$exists": True}},
        )

    def save_raw(
        self,
        image_id: uuid.UUID,
        data: bytes,
        shape: tuple[int, int],
        dtype: str,
        idempotency_key: str | None = None,
    ) -> uuid.UUID:
        if dtype not in ALLOWED_DTYPES:
            msg = f"Unsupported dtype: {dtype}"
            raise ValueError(msg)
        dt = np.dtype(dtype)
        expected = shape[0] * shape[1] * dt.itemsize
        if len(data) != expected:
            msg = f"Expected {expected} bytes for shape {shape} and dtype {dtype}, got {len(data)}"
            raise ValueError(msg)

        if idempotency_key is not None:
            existing = self._find_by_idempotency_key(idempotency_key)
            if existing is not None:
                return existing

        metadata = {"uuid": str(image_id), "shape": list(shape), "dtype": str(dt)}
        if idempotency_key is not None:
            metadata["idempotency_key"] = idempotency_key

        # Pass our own _id so we can clean up chunks if the files insert loses
        # a race on the idempotency index (GridFS writes chunks first).
        file_id = ObjectId()
        try:
            self.fs.put(data, _id=file_id, metadata=metadata, filename=str(image_id))
        except FileExists:
            self.fs.delete(file_id)  # removes orphaned chunks
            if idempotency_key is not None:
                existing = self._find_by_idempotency_key(idempotency_key)
                if existing is not None:
                    return existing
            raise

        return image_id

    def save_image(
        self, detector_image: DetectorImage, idempotency_key: str | None = None
    ) -> uuid.UUID:
        matrix = np.asarray(detector_image.values, dtype=np.float64).reshape(detector_image.shape)
        return self.save_raw(
            detector_image.id,
            matrix.tobytes(),
            tuple(matrix.shape),
            "float64",
            idempotency_key=idempotency_key,
        )

    def _find_by_idempotency_key(self, idempotency_key: str) -> uuid.UUID | None:
        doc = self._files.find_one({IDEMPOTENCY_FIELD: idempotency_key}, {"metadata.uuid": 1})
        if doc is None:
            return None
        return uuid.UUID(doc["metadata"]["uuid"])

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

    def get_image(self, id: uuid.UUID) -> DetectorImage:
        raw = self.open_raw(id)
        data = b"".join(raw.iter_chunks())
        matrix = np.frombuffer(data, dtype=raw.dtype).reshape(raw.shape)
        return DetectorImage(id=id, values=matrix.tolist(), shape=raw.shape)
