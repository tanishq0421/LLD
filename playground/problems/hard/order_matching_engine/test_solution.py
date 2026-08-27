"""Runnable tests for the Order Matching Engine. Write solution.py first."""
import unittest

try:
    from solution import OrderBook
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    OrderBook = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestResting(unittest.TestCase):
    def test_non_crossing_orders_rest(self):
        ob = OrderBook()
        self.assertEqual(ob.place_order("b1", "BUY", 10, 100), [])
        self.assertEqual(ob.best_bid(), 10)
        self.assertIsNone(ob.best_ask())
        self.assertEqual(ob.place_order("s1", "SELL", 12, 50), [])
        self.assertEqual(ob.best_ask(), 12)
        self.assertEqual(ob.open_quantity("b1"), 100)


class TestMatching(unittest.TestCase):
    def test_full_cross(self):
        ob = OrderBook()
        ob.place_order("b1", "BUY", 10, 100)
        trades = ob.place_order("s1", "SELL", 10, 100)
        self.assertEqual(trades, [{"buy_order": "b1", "sell_order": "s1",
                                   "price": 10, "quantity": 100}])
        self.assertIsNone(ob.best_bid())
        self.assertIsNone(ob.best_ask())
        self.assertEqual(ob.open_quantity("b1"), 0)

    def test_partial_fill_incoming_rests(self):
        ob = OrderBook()
        ob.place_order("s1", "SELL", 10, 60)
        trades = ob.place_order("b1", "BUY", 10, 100)   # buys 60, 40 rests
        self.assertEqual(trades, [{"buy_order": "b1", "sell_order": "s1",
                                   "price": 10, "quantity": 60}])
        self.assertEqual(ob.open_quantity("b1"), 40)
        self.assertEqual(ob.best_bid(), 10)
        self.assertIsNone(ob.best_ask())

    def test_trade_at_resting_price(self):
        ob = OrderBook()
        ob.place_order("b1", "BUY", 11, 100)            # resting bid at 11
        trades = ob.place_order("s1", "SELL", 10, 100)  # crosses; executes at resting 11
        self.assertEqual(trades[0]["price"], 11)

    def test_time_priority_fifo(self):
        ob = OrderBook()
        ob.place_order("b1", "BUY", 10, 100)            # older
        ob.place_order("b2", "BUY", 10, 100)            # newer, same price
        trades = ob.place_order("s1", "SELL", 10, 100)  # should fill b1 first
        self.assertEqual(trades, [{"buy_order": "b1", "sell_order": "s1",
                                   "price": 10, "quantity": 100}])
        self.assertEqual(ob.open_quantity("b1"), 0)
        self.assertEqual(ob.open_quantity("b2"), 100)

    def test_price_priority_across_levels(self):
        ob = OrderBook()
        ob.place_order("s1", "SELL", 10, 50)            # better ask
        ob.place_order("s2", "SELL", 11, 50)            # worse ask
        trades = ob.place_order("b1", "BUY", 11, 100)   # takes 50@10 then 50@11
        self.assertEqual(trades, [
            {"buy_order": "b1", "sell_order": "s1", "price": 10, "quantity": 50},
            {"buy_order": "b1", "sell_order": "s2", "price": 11, "quantity": 50},
        ])
        self.assertIsNone(ob.best_ask())
        self.assertEqual(ob.open_quantity("b1"), 0)

    def test_sell_matches_highest_bid_first(self):
        ob = OrderBook()
        ob.place_order("b1", "BUY", 9, 100)
        ob.place_order("b2", "BUY", 10, 100)            # better bid
        trades = ob.place_order("s1", "SELL", 9, 100)   # should hit b2 (10) first
        self.assertEqual(trades[0]["buy_order"], "b2")
        self.assertEqual(trades[0]["price"], 10)


class TestCancel(unittest.TestCase):
    def test_cancel_removes_resting(self):
        ob = OrderBook()
        ob.place_order("b1", "BUY", 10, 100)
        ob.cancel("b1")
        self.assertIsNone(ob.best_bid())
        self.assertEqual(ob.open_quantity("b1"), 0)

    def test_cancelled_order_not_matched(self):
        ob = OrderBook()
        ob.place_order("b1", "BUY", 10, 100)
        ob.cancel("b1")
        trades = ob.place_order("s1", "SELL", 10, 100)  # nothing to match -> rests
        self.assertEqual(trades, [])
        self.assertEqual(ob.best_ask(), 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
