"""Runnable tests for the Payment Gateway. Write solution.py first."""
import unittest

try:
    from solution import PaymentGateway, PaymentError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    PaymentGateway = PaymentError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestIdempotency(unittest.TestCase):
    def test_same_key_same_payment(self):
        g = PaymentGateway()
        p1 = g.charge("key-1", 100)
        p2 = g.charge("key-1", 100)     # retry
        self.assertEqual(p1, p2)

    def test_different_keys_different_payments(self):
        g = PaymentGateway()
        self.assertNotEqual(g.charge("k1", 100), g.charge("k2", 100))

    def test_retry_does_not_recharge_or_change_amount(self):
        g = PaymentGateway()
        p = g.charge("key-1", 100)
        g.charge("key-1", 999)          # retry with a different amount -> ignored
        g.capture(p)
        self.assertEqual(g.captured_amount(p), 100)   # original amount preserved


class TestLifecycle(unittest.TestCase):
    def setUp(self):
        self.g = PaymentGateway()
        self.p = self.g.charge("k", 100)

    def test_initial_authorized(self):
        self.assertEqual(self.g.status(self.p), "AUTHORIZED")

    def test_capture(self):
        self.assertEqual(self.g.capture(self.p), "CAPTURED")
        self.assertEqual(self.g.captured_amount(self.p), 100)

    def test_cannot_capture_twice(self):
        self.g.capture(self.p)
        with self.assertRaises(PaymentError):
            self.g.capture(self.p)

    def test_cannot_refund_before_capture(self):
        with self.assertRaises(PaymentError):
            self.g.refund(self.p, 50)

    def test_full_refund(self):
        self.g.capture(self.p)
        self.assertEqual(self.g.refund(self.p), "REFUNDED")   # None -> full
        self.assertEqual(self.g.amount_refunded(self.p), 100)

    def test_partial_then_full(self):
        self.g.capture(self.p)
        self.assertEqual(self.g.refund(self.p, 30), "PARTIALLY_REFUNDED")
        self.assertEqual(self.g.amount_refunded(self.p), 30)
        self.assertEqual(self.g.refund(self.p, 70), "REFUNDED")
        self.assertEqual(self.g.amount_refunded(self.p), 100)

    def test_over_refund_rejected(self):
        self.g.capture(self.p)
        self.g.refund(self.p, 60)
        with self.assertRaises(PaymentError):
            self.g.refund(self.p, 50)     # 60 + 50 > 100

    def test_unknown_payment(self):
        with self.assertRaises(PaymentError):
            self.g.status("nope")


if __name__ == "__main__":
    unittest.main(verbosity=2)
