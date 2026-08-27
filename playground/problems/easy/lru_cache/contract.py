"""
Test contract for the LRU Cache.

Your `solution.py` must define `LRUCache`:

    class LRUCache:
        def __init__(self, capacity: int):
            # capacity >= 1.

        def get(self, key):
            # Return the value and mark `key` most-recently-used.
            # Raise KeyError if the key is absent or was evicted.

        def put(self, key, value) -> None:
            # Insert or update. Mark most-recently-used.
            # If size exceeds capacity, evict the least-recently-used entry.

        def __len__(self) -> int:
            # Current number of live entries.

Both get and put should be O(1). How you achieve that (dict + doubly linked list, OrderedDict,
etc.) is your design.
"""
