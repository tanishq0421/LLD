"""Runnable tests for the Coffee Machine (Decorator). Write solution.py first."""
import unittest

try:
    from solution import CoffeeShop, MenuError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    CoffeeShop = MenuError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestCoffee(unittest.TestCase):
    def setUp(self):
        self.shop = CoffeeShop()

    def test_base_cost_and_description(self):
        b = self.shop.base("espresso")
        self.assertEqual(b.cost(), 2.0)
        self.assertEqual(b.description(), "Espresso")

    def test_single_addon(self):
        b = self.shop.add(self.shop.base("espresso"), "milk")
        self.assertEqual(b.cost(), 2.5)
        self.assertEqual(b.description(), "Espresso, Milk")

    def test_multiple_addons_in_order(self):
        b = self.shop.base("latte")
        b = self.shop.add(b, "milk")
        b = self.shop.add(b, "sugar")
        b = self.shop.add(b, "caramel")
        self.assertAlmostEqual(b.cost(), 3.0 + 0.5 + 0.25 + 0.75)
        self.assertEqual(b.description(), "Latte, Milk, Sugar, Caramel")

    def test_repeated_addon(self):
        b = self.shop.base("cappuccino")
        b = self.shop.add(b, "milk")
        b = self.shop.add(b, "milk")
        self.assertAlmostEqual(b.cost(), 3.5 + 1.0)
        self.assertEqual(b.description(), "Cappuccino, Milk, Milk")

    def test_unknown_base(self):
        with self.assertRaises(MenuError):
            self.shop.base("mocha")

    def test_unknown_addon(self):
        with self.assertRaises(MenuError):
            self.shop.add(self.shop.base("espresso"), "whip")

    def test_original_beverage_unchanged(self):
        base = self.shop.base("espresso")
        self.shop.add(base, "milk")           # decorating returns a NEW beverage
        self.assertEqual(base.cost(), 2.0)     # original not mutated
        self.assertEqual(base.description(), "Espresso")


if __name__ == "__main__":
    unittest.main(verbosity=2)
