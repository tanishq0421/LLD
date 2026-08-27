"""
Test contract for the in-memory KV store with nested transactions.

Your `solution.py` must define `KVStore` and a `NoTransaction` exception.

    class KVStore:
        def get(self, key):
            # Effective value (innermost layer down to base), or None if unset/deleted.

        def set(self, key, value) -> None:
            # Write into the innermost open transaction, or the base store if none is open.
            # Values are non-None.

        def delete(self, key) -> None:
            # Mark the key deleted in the innermost open transaction (or remove from base).
            # Deleting a missing key is a no-op.

        def count(self, value) -> int:
            # Number of keys whose current effective value == value.

        def begin(self) -> None:
            # Open a new (nestable) transaction layer.

        def commit(self) -> None:
            # Merge the innermost layer into its parent (or base) and close it.
            # Raise NoTransaction if no transaction is open.

        def rollback(self) -> None:
            # Discard the innermost layer's changes.
            # Raise NoTransaction if no transaction is open.

Recommended internal model: a base dict + a stack of overlay dicts, where an overlay may map a key
to a value or to a DELETED sentinel. (Implementation is yours; only the behavior above is tested.)
"""
