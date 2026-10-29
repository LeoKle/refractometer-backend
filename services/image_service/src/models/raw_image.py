from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol


class ByteSource(Protocol):
    """Anything that can be read in chunks. GridOut, open files, S3 bodies, BytesIO"""

    def read(self, size: int = -1) -> bytes: ...
    def close(self) -> None: ...


@dataclass(frozen=True)
class RawImage:
    stream: ByteSource
    shape: tuple[int, int]
    dtype: str
    length: int  # total bytes, for Content-Length

    def iter_chunks(self, chunk_size: int = 1024 * 1024) -> Iterator[bytes]:
        try:
            while chunk := self.stream.read(chunk_size):
                yield chunk
        finally:
            self.stream.close()
