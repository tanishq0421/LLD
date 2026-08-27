"""Runnable tests for the LRU Cache. Write solution.py first."""
import unittest

try:
    from solution import LRUCache
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    LRUCache = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestLRU(unittest.TestCase):
    def test_put_get(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        self.assertEqual(c.get("a"), 1)
        self.assertEqual(c.get("b"), 2)
        self.assertEqual(len(c), 2)

    def test_update_existing_key(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("a", 99)
        self.assertEqual(c.get("a"), 99)
        self.assertEqual(len(c), 1)

    def test_evicts_least_recently_used(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        c.put("c", 3)  # capacity 2 -> "a" (LRU) evicted
        with self.assertRaises(KeyError):
            c.get("a")
        self.assertEqual(c.get("b"), 2)
        self.assertEqual(c.get("c"), 3)
        self.assertEqual(len(c), 2)

    def test_get_refreshes_recency(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        self.assertEqual(c.get("a"), 1)  # "a" now MRU, "b" is LRU
        c.put("c", 3)                     # evicts "b", not "a"
        self.assertEqual(c.get("a"), 1)
        self.assertEqual(c.get("c"), 3)
        with self.assertRaises(KeyError):
            c.get("b")

    def test_put_refreshes_recency(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        c.put("a", 10)   # updating "a" makes it MRU
        c.put("c", 3)    # evicts "b"
        with self.assertRaises(KeyError):
            c.get("b")
        self.assertEqual(c.get("a"), 10)

    def test_missing_key_raises(self):
        c = LRUCache(1)
        with self.assertRaises(KeyError):
            c.get("nope")

    def test_capacity_one(self):
        c = LRUCache(1)
        c.put("a", 1)
        c.put("b", 2)  # evicts "a"
        self.assertEqual(c.get("b"), 2)
        self.assertEqual(len(c), 1)
        with self.assertRaises(KeyError):
            c.get("a")


if __name__ == "__main__":
    unittest.main(verbosity=2)
