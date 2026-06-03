import uuid

import numpy as np
from gridfs import GridFS
from pymongo.database import Database

from interfaces.image_repository_interface import ImageRepositoryInterface
from models.detector_image import DetectorImage


class ImageRepository(ImageRepositoryInterface):
    def __init__(self, db: Database):
        self.fs: GridFS = GridFS(db)

    def save_image(self, detector_image: DetectorImage):
        matrix = np.array(detector_image.values).reshape(detector_image.shape)

        metadata = {
            "uuid": str(detector_image.id),
            "shape": list(matrix.shape),
            "dtype": str(matrix.dtype),
        }

        self.fs.put(matrix.tobytes(), metadata=metadata, filename=str(detector_image.id))

    def get_image(self, id: uuid.UUID) -> DetectorImage:
        grid_out = self.fs.find_one({"metadata.uuid": str(id)})

        if grid_out is None:
            msg = f"Image with id {id} not found"
            raise FileNotFoundError(msg)

        image_bytes = grid_out.read()
        shape = tuple(grid_out.metadata["shape"])
        dtype = grid_out.metadata["dtype"]

        matrix = np.frombuffer(image_bytes, dtype=dtype).reshape(shape)

        return DetectorImage(
            id=id,
            values=matrix.tolist(),
            shape=shape,
        )
