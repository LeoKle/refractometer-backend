import uuid

import mongomock
import numpy as np
import pytest
from gridfs import GridFS
from mongomock.gridfs import enable_gridfs_integration

from models.detector_image import DetectorImage
from models.raw_image import RawImage
from repositories.image_repository import ImageRepository

enable_gridfs_integration()

IMAGE_SHAPE = (4, 4)


@pytest.fixture
def db():
    client = mongomock.MongoClient()
    return client["test_db"]


@pytest.fixture
def fs(db):
    return GridFS(db)


@pytest.fixture
def repo(db):
    return ImageRepository(db)


@pytest.fixture
def image():
    values = [[float(r * 4 + c) for c in range(4)] for r in range(4)]
    return DetectorImage(values=values, shape=IMAGE_SHAPE)


def read_all(raw: RawImage) -> bytes:
    return b"".join(raw.iter_chunks())


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


class TestSaveRaw:
    @pytest.mark.parametrize("dtype", ["float32", "float64", "uint8", "uint16", "int16", "int32"])
    def test_round_trip_for_each_allowed_dtype(self, repo, dtype):
        arr = (np.arange(12).reshape(3, 4)).astype(dtype)
        image_id = uuid.uuid4()

        repo.save_raw(image_id, arr.tobytes(), (3, 4), dtype)
        raw = repo.open_raw(image_id)

        assert raw.dtype == dtype
        assert raw.shape == (3, 4)
        recovered = np.frombuffer(read_all(raw), dtype=raw.dtype).reshape(raw.shape)
        np.testing.assert_array_equal(recovered, arr)

    def test_metadata_matches_legacy_layout(self, repo, fs):
        arr = np.zeros((2, 3), dtype=np.float32)
        image_id = uuid.uuid4()
        repo.save_raw(image_id, arr.tobytes(), (2, 3), "float32")

        grid_out = fs.find_one({"metadata.uuid": str(image_id)})
        assert grid_out.filename == str(image_id)
        assert grid_out.metadata == {
            "uuid": str(image_id),
            "shape": [2, 3],
            "dtype": "float32",
        }

    def test_unsupported_dtype_rejected(self, repo):
        with pytest.raises(ValueError, match="Unsupported dtype"):
            repo.save_raw(uuid.uuid4(), b"\x00" * 16, (2, 2), "object")

    def test_wrong_byte_count_rejected(self, repo):
        # 2x2 float32 needs 16 bytes
        with pytest.raises(ValueError, match="Expected 16 bytes"):
            repo.save_raw(uuid.uuid4(), b"\x00" * 15, (2, 2), "float32")

    def test_nothing_stored_when_validation_fails(self, repo, fs):
        image_id = uuid.uuid4()
        with pytest.raises(ValueError):
            repo.save_raw(image_id, b"\x00", (2, 2), "float32")
        assert fs.find_one({"metadata.uuid": str(image_id)}) is None


class TestOpenRaw:
    def test_returns_raw_image(self, repo):
        image_id = uuid.uuid4()
        repo.save_raw(image_id, np.zeros(4, dtype=np.uint8).tobytes(), (2, 2), "uint8")
        assert isinstance(repo.open_raw(image_id), RawImage)

    def test_length_matches_byte_count(self, repo):
        image_id = uuid.uuid4()
        data = np.zeros((3, 5), dtype=np.uint16).tobytes()
        repo.save_raw(image_id, data, (3, 5), "uint16")
        assert repo.open_raw(image_id).length == len(data)

    def test_raises_for_unknown_id(self, repo):
        with pytest.raises(FileNotFoundError):
            repo.open_raw(uuid.uuid4())

    def test_error_message_contains_id(self, repo):
        missing_id = uuid.uuid4()
        with pytest.raises(FileNotFoundError, match=str(missing_id)):
            repo.open_raw(missing_id)


class TestBackwardCompatibility:
    def test_document_written_in_original_format_is_readable(self, repo, fs):
        """Simulates a document stored by the pre-refactor repository."""
        image_id = uuid.uuid4()
        matrix = np.arange(6, dtype=np.float64).reshape(2, 3)
        fs.put(
            matrix.tobytes(),
            metadata={
                "uuid": str(image_id),
                "shape": list(matrix.shape),
                "dtype": str(matrix.dtype),
            },
            filename=str(image_id),
        )

        result = repo.get_image(image_id)
        assert result.shape == (2, 3)
        np.testing.assert_array_equal(np.array(result.values), matrix)

        raw = repo.open_raw(image_id)
        assert raw.dtype == "float64"
        assert raw.length == matrix.nbytes

    def test_image_saved_via_json_path_is_readable_as_raw(self, repo, image):
        repo.save_image(image)
        raw = repo.open_raw(image.id)
        recovered = np.frombuffer(read_all(raw), dtype=raw.dtype).reshape(raw.shape)
        np.testing.assert_array_equal(recovered, np.array(image.values))

    def test_image_saved_via_raw_path_is_readable_as_json(self, repo):
        image_id = uuid.uuid4()
        arr = np.arange(6, dtype=np.float32).reshape(2, 3)
        repo.save_raw(image_id, arr.tobytes(), (2, 3), "float32")

        result = repo.get_image(image_id)
        assert result.shape == (2, 3)
        np.testing.assert_array_equal(np.array(result.values), arr)
