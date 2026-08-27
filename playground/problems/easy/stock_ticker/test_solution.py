"""Runnable tests for the Stock Price Ticker (Observer). Write solution.py first."""
import unittest

try:
    from solution import Stock
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Stock = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class Recorder:
    """A simple observer that records the updates it receives."""
    def __init__(self):
        self.calls = []
    def update(self, symbol, old, new):
        self.calls.append((symbol, old, new))


class TestObserver(unittest.TestCase):
    def setUp(self):
        self.stock = Stock("AAPL", 100.0)

    def test_notify_on_change(self):
        r = Recorder()
        self.stock.subscribe(r)
        self.stock.set_price(101.0)
        self.assertEqual(r.calls, [("AAPL", 100.0, 101.0)])
        self.assertEqual(self.stock.price, 101.0)

    def test_multiple_observers(self):
        r1, r2 = Recorder(), Recorder()
        self.stock.subscribe(r1)
        self.stock.subscribe(r2)
        self.stock.set_price(105.0)
        self.assertEqual(r1.calls, [("AAPL", 100.0, 105.0)])
        self.assertEqual(r2.calls, [("AAPL", 100.0, 105.0)])

    def test_no_notify_when_unchanged(self):
        r = Recorder()
        self.stock.subscribe(r)
        self.stock.set_price(100.0)   # same value
        self.assertEqual(r.calls, [])

    def test_unsubscribe(self):
        r = Recorder()
        self.stock.subscribe(r)
        self.stock.set_price(101.0)
        self.stock.unsubscribe(r)
        self.stock.set_price(102.0)
        self.assertEqual(r.calls, [("AAPL", 100.0, 101.0)])  # no second update

    def test_subscribe_is_idempotent(self):
        r = Recorder()
        self.stock.subscribe(r)
        self.stock.subscribe(r)       # second subscribe should not duplicate
        self.stock.set_price(101.0)
        self.assertEqual(len(r.calls), 1)

    def test_sequence_of_changes(self):
        r = Recorder()
        self.stock.subscribe(r)
        self.stock.set_price(101.0)
        self.stock.set_price(103.0)
        self.assertEqual(r.calls, [("AAPL", 100.0, 101.0), ("AAPL", 101.0, 103.0)])

    def test_unsubscribe_unknown_is_noop(self):
        self.stock.unsubscribe(Recorder())   # should not raise


if __name__ == "__main__":
    unittest.main(verbosity=2)
