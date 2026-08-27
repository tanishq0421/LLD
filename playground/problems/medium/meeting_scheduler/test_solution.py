"""Runnable tests for the Meeting Room Scheduler. Write solution.py first."""
import unittest

try:
    from solution import MeetingScheduler, Conflict, NoRoomAvailable
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    MeetingScheduler = Conflict = NoRoomAvailable = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


def sched(rooms=("R1", "R2")):
    s = MeetingScheduler()
    for r in rooms:
        s.add_room(r)
    return s


class TestBooking(unittest.TestCase):
    def test_book_returns_id(self):
        s = sched()
        self.assertIsNotNone(s.book("R1", 10, 11))

    def test_overlap_conflicts(self):
        s = sched()
        s.book("R1", 10, 12)
        with self.assertRaises(Conflict):
            s.book("R1", 11, 13)

    def test_back_to_back_allowed(self):
        s = sched()
        s.book("R1", 10, 11)
        self.assertIsNotNone(s.book("R1", 11, 12))   # adjacent, no overlap

    def test_non_overlapping_allowed(self):
        s = sched()
        s.book("R1", 10, 11)
        self.assertIsNotNone(s.book("R1", 13, 14))

    def test_same_interval_other_room_ok(self):
        s = sched()
        s.book("R1", 10, 11)
        self.assertIsNotNone(s.book("R2", 10, 11))

    def test_invalid_interval(self):
        s = sched()
        with self.assertRaises(ValueError):
            s.book("R1", 11, 11)
        with self.assertRaises(ValueError):
            s.book("R1", 12, 10)

    def test_unknown_room(self):
        s = sched()
        with self.assertRaises(KeyError):
            s.book("R9", 10, 11)


class TestAvailability(unittest.TestCase):
    def test_is_available(self):
        s = sched()
        s.book("R1", 10, 12)
        self.assertFalse(s.is_available("R1", 11, 13))
        self.assertTrue(s.is_available("R1", 12, 13))

    def test_available_rooms(self):
        s = sched()
        s.book("R1", 10, 12)
        self.assertEqual(s.available_rooms(10, 12), ["R2"])
        self.assertEqual(s.available_rooms(13, 14), ["R1", "R2"])

    def test_book_any(self):
        s = sched()
        s.book("R1", 10, 12)               # R1 busy
        room, bid = s.book_any(10, 12)     # -> R2
        self.assertEqual(room, "R2")
        self.assertIsNotNone(bid)

    def test_book_any_none_available(self):
        s = sched(("R1",))
        s.book("R1", 10, 12)
        with self.assertRaises(NoRoomAvailable):
            s.book_any(11, 13)

    def test_cancel_frees_slot(self):
        s = sched()
        bid = s.book("R1", 10, 12)
        s.cancel(bid)
        self.assertTrue(s.is_available("R1", 10, 12))
        self.assertIsNotNone(s.book("R1", 10, 12))

    def test_cancel_unknown(self):
        s = sched()
        with self.assertRaises(KeyError):
            s.cancel("nope")


if __name__ == "__main__":
    unittest.main(verbosity=2)
