# ISP applied: split the one fat interface into small ROLE interfaces.
# Each storage inherits only the roles it can actually honour, and each
# client asks for only the role it actually needs.
#
# Note the multiple inheritance below - this is the legitimate "mixin"
# use of it: several tiny single-purpose bases combined into one concrete
# class, not a deep hierarchy.

from abc import ABC, abstractmethod
from typing import Any


class Readable(ABC):
    @abstractmethod
    def read_data(self, data_id: str) -> str:
        """Return the stored payload for data_id."""


class Writable(ABC):
    @abstractmethod
    def write_data(self, data_id: str, data: str) -> None:
        """Store data under data_id."""


class Deletable(ABC):
    @abstractmethod
    def delete_data(self, data_id: str) -> None:
        """Remove data_id from the store."""


class Configurable(ABC):
    @abstractmethod
    def show_config(self, data_id: str) -> dict[str, Any]:
        """Return the bucket configuration as a dict."""
        # -> dict[str, Any], NOT '-> json'. json is a MODULE, not a type;
        #    a checker rejects it and it never says whether you get back a
        #    serialised str or a parsed dict.


class BaseStorage:
    # Shared state only. Deliberately holds no abstract methods, so it
    # forces nothing on anybody.
    def __init__(self, storage_name: str, capacity: float):
        self._storage_name = storage_name
        self._capacity = capacity


class S3Storage(BaseStorage, Readable, Writable, Deletable, Configurable):
    # Opts into all four roles because it genuinely supports all four.
    def read_data(self, data_id: str) -> str:
        print(f"Reading data from S3: {data_id}")
        return f"Data for {data_id} from S3"

    def write_data(self, data_id: str, data: str) -> None:
        print(f"Writing data to S3: {data_id} -> {data}")

    def delete_data(self, data_id: str) -> None:
        print(f"Deleting data from S3: {data_id}")

    def show_config(self, data_id: str) -> dict[str, Any]:
        return {"bucket": self._storage_name, "versioning": True, "region": "ap-south-1"}


class GlacierStorage(BaseStorage, Readable, Writable):
    # Opts into two roles. No delete_data, no show_config - and crucially
    # no stubs, no NotImplementedError, no lying about what it can do.
    def read_data(self, data_id: str) -> str:
        print(f"Restoring archive from Glacier: {data_id}")
        return f"Archived data for {data_id}"

    def write_data(self, data_id: str, data: str) -> None:
        print(f"Archiving to Glacier: {data_id} -> {data}")


class CdnCache(BaseStorage, Readable):
    # A brand new read-only source. Slots in without touching a single
    # existing line - that is the extensibility ISP buys you.
    def read_data(self, data_id: str) -> str:
        print(f"Serving from CDN edge: {data_id}")
        return f"Cached copy of {data_id}"


# ---- the client side: ask for the narrowest role that does the job ----
def render_report(store: Readable) -> None:
    # Cannot call delete_data even by accident - it is not in the type.
    print(f"  report says: {store.read_data('report-1')}")


def purge(store: Deletable, data_id: str) -> None:
    store.delete_data(data_id)


s3 = S3Storage("my-bucket", 500.0)
glacier = GlacierStorage("cold-archive", 5000.0)
cdn = CdnCache("edge-cache", 50.0)

print("--- one read-only client, three different storages ---")
for store in (s3, glacier, cdn):
    render_report(store)

print("\n--- only the storages that CAN delete are ever passed to purge ---")
purge(s3, "cfg-1")
# purge(glacier, "cfg-1")   # a type checker rejects this line before it runs

print("\n--- Configurable is asked of the only class that offers it ---")
print(f"config: {s3.show_config('cfg-1')}")

print("""
What changed:
  * GlacierStorage no longer stubs methods it cannot honour
  * render_report accepts anything Readable, including CdnCache which did
    not exist when it was written
  * misuse (purge(glacier, ...)) is now a TYPE ERROR, not a runtime crash

ISP is about BOTH sides:
  implementers inherit only roles they can honour,
  clients depend only on the role they call.
""")
