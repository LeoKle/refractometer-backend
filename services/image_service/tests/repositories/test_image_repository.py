import uuid

import mongomock
import numpy as np
import pytest
from mongomock.gridfs import enable_gridfs_integration

from models.detector_image import DetectorImage
from repositories.image_repository import ImageRepository

enable_gridfs_integration()

IMAGE_SHAPE = (4, 4)


@pytest.fixture
def db():
    client = mongomock.MongoClient()
    return client["test_db"]


@pytest.fixture
def repo(db):
    return ImageRepository(db)


@pytest.fixture
def image():
    values = [[float(r * 4 + c) for c in range(4)] for r in range(4)]
    return DetectorImage(values=values, shape=IMAGE_SHAPE)


class TestSaveImage:
    def test_file_exists_in_gridfs_after_save(self, repo, db, image):
        repo.save_image(image)
        from gridfs import GridFS

        fs = GridFS(db)
        grid_out = fs.find_one({"metadata.uuid": str(image.id)})
        assert grid_out is not None

    def test_metadata_shape_stored_correctly(self, repo, db, image):
        repo.save_image(image)
        from gridfs import GridFS

        grid_out = GridFS(db).find_one({"metadata.uuid": str(image.id)})
        assert tuple(grid_out.metadata["shape"]) == IMAGE_SHAPE

    def test_metadata_dtype_stored(self, repo, db, image):
        repo.save_image(image)
        from gridfs import GridFS

        grid_out = GridFS(db).find_one({"metadata.uuid": str(image.id)})
        assert "dtype" in grid_out.metadata

    def test_filename_is_uuid_string(self, repo, db, image):
        repo.save_image(image)
        from gridfs import GridFS

        grid_out = GridFS(db).find_one({"metadata.uuid": str(image.id)})
        assert grid_out.filename == str(image.id)


class TestGetImage:
    def test_returns_detector_image_instance(self, repo, image):
        repo.save_image(image)
        result = repo.get_image(image.id)
        assert isinstance(result, DetectorImage)

    def test_id_preserved(self, repo, image):
        repo.save_image(image)
        result = repo.get_image(image.id)
        assert result.id == image.id

    def test_shape_preserved(self, repo, image):
        repo.save_image(image)
        result = repo.get_image(image.id)
        assert result.shape == IMAGE_SHAPE

    def test_values_preserved(self, repo, image):
        repo.save_image(image)
        result = repo.get_image(image.id)
        original = np.array(image.values)
        recovered = np.array(result.values)
        np.testing.assert_array_almost_equal(original, recovered)

    def test_raises_for_unknown_id(self, repo):
        with pytest.raises(FileNotFoundError):
            repo.get_image(uuid.uuid4())

    def test_error_message_contains_id(self, repo):
        missing_id = uuid.uuid4()
        with pytest.raises(FileNotFoundError, match=str(missing_id)):
            repo.get_image(missing_id)


class TestRoundTrip:
    def test_multiple_images_stored_independently(self, repo):
        img_a = DetectorImage(values=[[1.0, 2.0], [3.0, 4.0]], shape=(2, 2))
        img_b = DetectorImage(values=[[9.0, 8.0], [7.0, 6.0]], shape=(2, 2))

        repo.save_image(img_a)
        repo.save_image(img_b)

        result_a = repo.get_image(img_a.id)
        result_b = repo.get_image(img_b.id)

        np.testing.assert_array_almost_equal(np.array(result_a.values), np.array(img_a.values))
        np.testing.assert_array_almost_equal(np.array(result_b.values), np.array(img_b.values))

    def test_non_square_shape_preserved(self, repo):
        values = [[float(i) for i in range(6)] for _ in range(2)]
        img = DetectorImage(values=values, shape=(2, 6))
        repo.save_image(img)
        result = repo.get_image(img.id)
        assert result.shape == (2, 6)
        np.testing.assert_array_almost_equal(np.array(result.values), np.array(values))

    def test_zero_matrix_round_trips(self, repo):
        values = [[0.0] * 3 for _ in range(3)]
        img = DetectorImage(values=values, shape=(3, 3))
        repo.save_image(img)
        result = repo.get_image(img.id)
        np.testing.assert_array_equal(np.array(result.values), np.zeros((3, 3)))

    def test_negative_values_round_trip(self, repo):
        values = [[-1.5, -2.5], [-3.5, -4.5]]
        img = DetectorImage(values=values, shape=(2, 2))
        repo.save_image(img)
        result = repo.get_image(img.id)
        np.testing.assert_array_almost_equal(np.array(result.values), np.array(values))
