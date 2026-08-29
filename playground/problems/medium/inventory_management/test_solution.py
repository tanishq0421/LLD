"""Runnable tests for the Inventory Management system. Write solution.py first."""
import unittest

try:
    from solution import Inventory, InventoryError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Inventory = InventoryError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestReserveLifecycle(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory()
        self.inv.add_product("sku1", 10)

    def test_available_initial(self):
        self.assertEqual(self.inv.available("sku1"), 10)

    def test_reserve_reduces_available_not_onhand(self):
        self.inv.reserve("sku1", 3)
        self.assertEqual(self.inv.available("sku1"), 7)

    def test_confirm_reduces_onhand(self):
        r = self.inv.reserve("sku1", 4)
        self.inv.confirm(r)
        self.assertEqual(self.inv.available("sku1"), 6)   # 10 - 4 committed
        # re-reserving should now see 6
        self.inv.reserve("sku1", 6)
        self.assertEqual(self.inv.available("sku1"), 0)

    def test_release_returns_availability(self):
        r = self.inv.reserve("sku1", 4)
        self.assertEqual(self.inv.available("sku1"), 6)
        self.inv.release(r)
        self.assertEqual(self.inv.available("sku1"), 10)

    def test_reserve_insufficient(self):
        self.inv.reserve("sku1", 8)
        with self.assertRaises(InventoryError):
            self.inv.reserve("sku1", 5)     # only 2 available

    def test_restock(self):
        self.inv.restock("sku1", 5)
        self.assertEqual(self.inv.available("sku1"), 15)


class TestGuards(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory()
        self.inv.add_product("sku1", 5)

    def test_unknown_sku(self):
        with self.assertRaises(InventoryError):
            self.inv.available("ghost")
        with self.assertRaises(InventoryError):
            self.inv.reserve("ghost", 1)

    def test_double_confirm(self):
        r = self.inv.reserve("sku1", 1)
        self.inv.confirm(r)
        with self.assertRaises(InventoryError):
            self.inv.confirm(r)

    def test_release_after_confirm(self):
        r = self.inv.reserve("sku1", 1)
        self.inv.confirm(r)
        with self.assertRaises(InventoryError):
            self.inv.release(r)

    def test_unknown_reservation(self):
        with self.assertRaises(InventoryError):
            self.inv.confirm("nope")


@unittest.skip("Follow-up: concurrency. Remove this skip once reserve() is thread-safe.")
class TestConcurrency(unittest.TestCase):
    def test_no_oversell(self):
        import threading
        inv = Inventory()
        inv.add_product("hot", 50)          # 50 units
        ok = []
        lock = threading.Lock()

        def worker():
            try:
                inv.reserve("hot", 1)
                with lock:
                    ok.append(1)
            except InventoryError:
                pass

        threads = [threading.Thread(target=worker) for _ in range(200)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(sum(ok), 50)       # exactly 50 reservations succeed
        self.assertEqual(inv.available("hot"), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
