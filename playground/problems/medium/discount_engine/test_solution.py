"""Runnable tests for the Discount Engine. Write solution.py first."""
import unittest

try:
    from solution import Cart, DiscountEngine
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Cart = DiscountEngine = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


def cart_of(total):
    c = Cart()
    c.add_item("thing", total, 1)
    return c


class TestCart(unittest.TestCase):
    def test_subtotal(self):
        c = Cart()
        c.add_item("a", 10, 2)
        c.add_item("b", 5, 1)
        self.assertEqual(c.subtotal(), 25)


class TestRules(unittest.TestCase):
    def test_percentage(self):
        e = DiscountEngine()
        e.add_rule(DiscountEngine.percentage(10))
        self.assertEqual(e.total(cart_of(100)), 90.0)

    def test_flat(self):
        e = DiscountEngine()
        e.add_rule(DiscountEngine.flat(20))
        self.assertEqual(e.total(cart_of(100)), 80.0)

    def test_flat_floors_at_zero(self):
        e = DiscountEngine()
        e.add_rule(DiscountEngine.flat(200))
        self.assertEqual(e.total(cart_of(100)), 0.0)

    def test_threshold_applies(self):
        e = DiscountEngine()
        e.add_rule(DiscountEngine.threshold(500, 50))
        self.assertEqual(e.total(cart_of(600)), 550.0)

    def test_threshold_skipped(self):
        e = DiscountEngine()
        e.add_rule(DiscountEngine.threshold(500, 50))
        self.assertEqual(e.total(cart_of(400)), 400.0)

    def test_no_rules_is_subtotal(self):
        e = DiscountEngine()
        self.assertEqual(e.total(cart_of(123)), 123.0)


class TestStacking(unittest.TestCase):
    def test_percentage_then_flat(self):
        e = DiscountEngine()
        e.add_rule(DiscountEngine.percentage(10))   # 100 -> 90
        e.add_rule(DiscountEngine.flat(5))          # 90 -> 85
        self.assertEqual(e.total(cart_of(100)), 85.0)

    def test_order_matters(self):
        e = DiscountEngine()
        e.add_rule(DiscountEngine.flat(5))          # 100 -> 95
        e.add_rule(DiscountEngine.percentage(10))   # 95 -> 85.5
        self.assertEqual(e.total(cart_of(100)), 85.5)

    def test_custom_rule_pluggable(self):
        e = DiscountEngine()
        # a custom rule: knock the total down to a round number
        e.add_rule(lambda cart, t: t - (t % 10))
        self.assertEqual(e.total(cart_of(97)), 90.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
