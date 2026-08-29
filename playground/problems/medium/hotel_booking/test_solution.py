"""Runnable tests for the Hotel Booking System. Write solution.py first."""
import unittest

try:
    from solution import Hotel, Conflict, NoRoomAvailable
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Hotel = Conflict = NoRoomAvailable = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


def hotel():
    h = Hotel()
    h.add_room("101", "standard")
    h.add_room("102", "standard")
    h.add_room("201", "deluxe")
    return h


class TestBooking(unittest.TestCase):
    def test_book_and_availability(self):
        h = hotel()
        h.book("101", "alice", 10, 12)
        self.assertFalse(h.is_available("101", 11, 13))
        self.assertTrue(h.is_available("101", 12, 14))   # checkout day frees it

    def test_overlap_conflict(self):
        h = hotel()
        h.book("101", "alice", 10, 12)
        with self.assertRaises(Conflict):
            h.book("101", "bob", 11, 13)

    def test_back_to_back_allowed(self):
        h = hotel()
        h.book("101", "alice", 10, 12)
        self.assertIsNotNone(h.book("101", "bob", 12, 14))

    def test_invalid_dates(self):
        h = hotel()
        with self.assertRaises(ValueError):
            h.book("101", "x", 12, 12)
        with self.assertRaises(ValueError):
            h.book("101", "x", 14, 10)

    def test_unknown_room(self):
        h = hotel()
        with self.assertRaises(KeyError):
            h.book("999", "x", 10, 12)


class TestSearch(unittest.TestCase):
    def test_find_available_by_type(self):
        h = hotel()
        h.book("101", "alice", 10, 12)
        self.assertEqual(h.find_available("standard", 10, 12), ["102"])
        self.assertEqual(h.find_available("standard", 12, 14), ["101", "102"])
        self.assertEqual(h.find_available("deluxe", 10, 12), ["201"])

    def test_book_any(self):
        h = hotel()
        h.book("101", "alice", 10, 12)
        room, bid = h.book_any("standard", 10, 12)   # 101 busy -> 102
        self.assertEqual(room, "102")
        self.assertIsNotNone(bid)

    def test_book_any_none(self):
        h = hotel()
        h.book("201", "alice", 10, 12)
        with self.assertRaises(NoRoomAvailable):
            h.book_any("deluxe", 11, 13)

    def test_cancel_frees_dates(self):
        h = hotel()
        bid = h.book("101", "alice", 10, 12)
        h.cancel(bid)
        self.assertTrue(h.is_available("101", 10, 12))

    def test_cancel_unknown(self):
        h = hotel()
        with self.assertRaises(KeyError):
            h.cancel("nope")


if __name__ == "__main__":
    unittest.main(verbosity=2)
