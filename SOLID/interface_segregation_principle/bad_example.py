# ISP: "No client should be forced to depend on methods it does not use."
#
# Here ONE fat interface declares everything any storage might ever do.
# S3 is happy - it really does all four. Glacier is not: it is an archive,
# so it has no config panel and cannot delete on demand. But the interface
# forces it to implement both anyway.

from abc import ABC, abstractmethod
from typing import Any


class CloudStorage(ABC):
    def __init__(self, storage_name: str, capacity: float):
        self._storage_name = storage_name
        self._capacity = capacity

    @abstractmethod
    def read_data(self, data_id: str) -> str:
        """Return the stored payload for data_id."""

    @abstractmethod
    def write_data(self, data_id: str, data: str) -> None:
        """Store data under data_id."""

    @abstractmethod
    def delete_data(self, data_id: str) -> None:
        """Remove data_id from the store."""

    @abstractmethod
    def show_config(self, data_id: str) -> dict[str, Any]:
        """Return the bucket configuration as a dict."""


class S3Storage(CloudStorage):
    # Fine - S3 genuinely supports all four operations.
    def read_data(self, data_id: str) -> str:
        print(f"Reading data from S3: {data_id}")
        return f"Data for {data_id} from S3"

    def write_data(self, data_id: str, data: str) -> None:
        print(f"Writing data to S3: {data_id} -> {data}")

    def delete_data(self, data_id: str) -> None:
        print(f"Deleting data from S3: {data_id}")

    def show_config(self, data_id: str) -> dict[str, Any]:
        return {"bucket": self._storage_name, "versioning": True, "region": "ap-south-1"}


class GlacierStorage(CloudStorage):
    # THE VIOLATION. Glacier is archival storage. It can read and write,
    # but it has no instant delete and no config panel. The fat interface
    # still forces both on it, so it must write stubs that lie or crash.
    def read_data(self, data_id: str) -> str:
        print(f"Restoring archive from Glacier: {data_id}")
        return f"Archived data for {data_id}"

    def write_data(self, data_id: str, data: str) -> None:
        print(f"Archiving to Glacier: {data_id} -> {data}")

    def delete_data(self, data_id: str) -> None:
        raise NotImplementedError("Glacier archives are immutable")   # forced stub

    def show_config(self, data_id: str) -> dict[str, Any]:
        raise NotImplementedError("Glacier has no config panel")      # forced stub


# A client that only ever READS. It still has to accept the whole fat
# interface, so nothing stops it from calling delete_data by mistake.
def render_report(store: CloudStorage) -> None:
    print(f"  report says: {store.read_data('report-1')}")


s3 = S3Storage("my-bucket", 500.0)
glacier = GlacierStorage("cold-archive", 5000.0)

print("--- S3 implements everything, no problem ---")
s3.write_data("cfg-1", "hello")
print(f"config: {s3.show_config('cfg-1')}")
s3.delete_data("cfg-1")

print("\n--- Glacier was forced to implement methods it does not have ---")
render_report(glacier)          # this part is fine
try:
    glacier.show_config("cfg-1")
except NotImplementedError as e:
    print(f"  crashed: {e}")    # a 'CloudStorage' that isn't really one

print("""
Two smells, both caused by the fat interface:
  * the IMPLEMENTER is forced to stub methods it has no use for
  * the CLIENT (render_report) only needs read_data, but depends on all four
""")
