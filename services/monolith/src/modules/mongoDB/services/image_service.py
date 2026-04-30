import numpy as np
from bson import ObjectId
from gridfs import GridFS
from pymongo.database import Database

from custom_types.detector_image import DetectorImage
from interfaces.database.services.image_service_interface import IImageService


class ImageService(IImageService):
    def __init__(self, db: Database):
        self.fs: GridFS = GridFS(db)

    def save_image(self, detector_image: DetectorImage) -> ObjectId:
        matrix = np.array(detector_image.values).reshape(detector_image.shape)

        metadata = {"shape": matrix.shape, "dtype": str(matrix.dtype)}
        file_id: ObjectId = self.fs.put(matrix.tobytes(), metadata=metadata)

        return file_id

    def retrieve_image(self, image_id: str) -> DetectorImage:
        image_data = self.fs.get(ObjectId(image_id))

        image_bytes = image_data.read()

        shape = image_data.metadata["shape"]
        dtype = image_data.metadata["dtype"]

        image = np.frombuffer(image_bytes, dtype=dtype).reshape(shape)

        return DetectorImage.fromNumpyArray(image)
