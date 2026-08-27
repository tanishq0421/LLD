"""Runnable tests for the Vending Machine. Write solution.py first."""
import unittest

try:
    from solution import VendingMachine, VendingError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    VendingMachine = VendingError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestHappyPath(unittest.TestCase):
    def setUp(self):
        self.m = VendingMachine()
        self.m.add_product("A1", "Water", price=15, quantity=2)
        self.m.add_product("A2", "Chips", price=25, quantity=1)

    def test_dispense_with_change(self):
        self.m.select("A1")
        self.m.insert_coin(10)
        self.m.insert_coin(10)
        name, change = self.m.dispense()
        self.assertEqual(name, "Water")
        self.assertEqual(change, 5)
        self.assertEqual(self.m.balance, 0)
        self.assertEqual(self.m.state, "IDLE")

    def test_exact_change(self):
        self.m.select("A2")
        self.m.insert_coin(10)
        self.m.insert_coin(10)
        self.m.insert_coin(5)
        name, change = self.m.dispense()
        self.assertEqual((name, change), ("Chips", 0))

    def test_inventory_decrements_and_runs_out(self):
        # Chips has qty 1 — second buyer must be rejected at select().
        self.m.select("A2")
        for c in (10, 10, 5):
            self.m.insert_coin(c)
        self.m.dispense()
        with self.assertRaises(VendingError):
            self.m.select("A2")

    def test_balance_accumulates(self):
        self.m.insert_coin(5)
        self.m.insert_coin(10)
        self.assertEqual(self.m.balance, 15)

    def test_starts_idle(self):
        self.assertEqual(self.m.state, "IDLE")


class TestGuards(unittest.TestCase):
    def setUp(self):
        self.m = VendingMachine()
        self.m.add_product("A1", "Water", price=15, quantity=1)

    def test_invalid_code(self):
        with self.assertRaises(VendingError):
            self.m.select("NOPE")

    def test_insufficient_balance(self):
        self.m.select("A1")
        self.m.insert_coin(10)
        with self.assertRaises(VendingError):
            self.m.dispense()
        # balance should be preserved after a failed dispense
        self.assertEqual(self.m.balance, 10)

    def test_dispense_without_selection(self):
        self.m.insert_coin(10)
        self.m.insert_coin(5)
        with self.assertRaises(VendingError):
            self.m.dispense()

    def test_refund_returns_balance_and_resets(self):
        self.m.select("A1")
        self.m.insert_coin(10)
        self.m.insert_coin(10)
        refunded = self.m.refund()
        self.assertEqual(refunded, 20)
        self.assertEqual(self.m.balance, 0)
        self.assertEqual(self.m.state, "IDLE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
