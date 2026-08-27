"""Runnable tests for the in-memory KV store. Write solution.py first."""
import unittest

try:
    from solution import KVStore, NoTransaction
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    KVStore = NoTransaction = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestBasic(unittest.TestCase):
    def test_set_get(self):
        kv = KVStore()
        kv.set("a", 1)
        self.assertEqual(kv.get("a"), 1)

    def test_get_missing_is_none(self):
        self.assertIsNone(KVStore().get("nope"))

    def test_delete(self):
        kv = KVStore()
        kv.set("a", 1)
        kv.delete("a")
        self.assertIsNone(kv.get("a"))

    def test_delete_missing_is_noop(self):
        kv = KVStore()
        kv.delete("ghost")  # should not raise
        self.assertIsNone(kv.get("ghost"))

    def test_count(self):
        kv = KVStore()
        kv.set("a", 10)
        kv.set("b", 10)
        kv.set("c", 20)
        self.assertEqual(kv.count(10), 2)
        self.assertEqual(kv.count(20), 1)
        self.assertEqual(kv.count(99), 0)


class TestTransactions(unittest.TestCase):
    def test_rollback_reverts(self):
        kv = KVStore()
        kv.set("a", 1)
        kv.begin()
        kv.set("a", 2)
        self.assertEqual(kv.get("a"), 2)  # visible inside txn
        kv.rollback()
        self.assertEqual(kv.get("a"), 1)  # reverted

    def test_commit_persists(self):
        kv = KVStore()
        kv.set("a", 1)
        kv.begin()
        kv.set("a", 2)
        kv.commit()
        self.assertEqual(kv.get("a"), 2)

    def test_delete_in_txn_then_rollback(self):
        kv = KVStore()
        kv.set("a", 1)
        kv.begin()
        kv.delete("a")
        self.assertIsNone(kv.get("a"))
        kv.rollback()
        self.assertEqual(kv.get("a"), 1)

    def test_commit_without_txn_raises(self):
        with self.assertRaises(NoTransaction):
            KVStore().commit()

    def test_rollback_without_txn_raises(self):
        with self.assertRaises(NoTransaction):
            KVStore().rollback()

    def test_new_key_in_txn_rolled_back(self):
        kv = KVStore()
        kv.begin()
        kv.set("x", 5)
        kv.rollback()
        self.assertIsNone(kv.get("x"))


class TestNesting(unittest.TestCase):
    def test_nested_rollback_only_inner(self):
        kv = KVStore()
        kv.set("a", 1)
        kv.begin()
        kv.set("a", 2)
        kv.begin()
        kv.set("a", 3)
        self.assertEqual(kv.get("a"), 3)
        kv.rollback()               # discard inner
        self.assertEqual(kv.get("a"), 2)
        kv.commit()                 # persist outer
        self.assertEqual(kv.get("a"), 2)

    def test_commit_merges_one_level(self):
        kv = KVStore()
        kv.begin()                  # outer
        kv.set("x", 1)
        kv.begin()                  # inner
        kv.set("x", 2)
        kv.commit()                 # inner merges into outer
        self.assertEqual(kv.get("x"), 2)
        kv.rollback()               # discard outer -> x gone
        self.assertIsNone(kv.get("x"))

    def test_count_respects_transactions(self):
        kv = KVStore()
        kv.set("a", 10)
        kv.begin()
        kv.set("b", 10)
        self.assertEqual(kv.count(10), 2)
        kv.rollback()
        self.assertEqual(kv.count(10), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
