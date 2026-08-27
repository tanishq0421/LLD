"""Runnable tests for BookMyShow. Write solution.py first."""
import unittest

try:
    from solution import BookingService, SeatUnavailable
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    BookingService = SeatUnavailable = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


def service():
    s = BookingService()
    s.add_show("show1", ["A1", "A2", "A3", "A4", "A5"])
    return s


class TestBooking(unittest.TestCase):
    def test_available_seats_initial(self):
        s = service()
        self.assertEqual(s.available_seats("show1"), ["A1", "A2", "A3", "A4", "A5"])

    def test_book_removes_from_available(self):
        s = service()
        bid = s.book("show1", ["A1", "A2"], "u1")
        self.assertIsNotNone(bid)
        self.assertEqual(s.available_seats("show1"), ["A3", "A4", "A5"])

    def test_double_book_rejected(self):
        s = service()
        s.book("show1", ["A1"], "u1")
        with self.assertRaises(SeatUnavailable):
            s.book("show1", ["A1"], "u2")

    def test_booking_is_all_or_nothing(self):
        s = service()
        s.book("show1", ["A2"], "u1")
        # A2 taken -> booking [A1, A2] must fail AND leave A1 still available
        with self.assertRaises(SeatUnavailable):
            s.book("show1", ["A1", "A2"], "u2")
        self.assertIn("A1", s.available_seats("show1"))

    def test_cancel_frees_seats(self):
        s = service()
        bid = s.book("show1", ["A1", "A2"], "u1")
        s.cancel(bid)
        self.assertEqual(s.available_seats("show1"), ["A1", "A2", "A3", "A4", "A5"])

    def test_get_booking(self):
        s = service()
        bid = s.book("show1", ["A3"], "u9")
        info = s.get_booking(bid)
        self.assertEqual(info["user_id"], "u9")
        self.assertEqual(sorted(info["seats"]), ["A3"])
        self.assertEqual(info["show_id"], "show1")


class TestGuards(unittest.TestCase):
    def test_unknown_show(self):
        s = service()
        with self.assertRaises(KeyError):
            s.available_seats("ghost")
        with self.assertRaises(KeyError):
            s.book("ghost", ["A1"], "u1")

    def test_unknown_seat(self):
        s = service()
        with self.assertRaises(KeyError):
            s.book("show1", ["Z9"], "u1")

    def test_cancel_unknown_booking(self):
        s = service()
        with self.assertRaises(KeyError):
            s.cancel("nope")


@unittest.skip("Follow-up: concurrency. Remove this skip once book() is thread-safe.")
class TestConcurrency(unittest.TestCase):
    def test_only_one_wins_the_same_seat(self):
        import threading
        s = BookingService()
        s.add_show("show1", ["A1"])          # a single hot seat
        results = []
        rlock = threading.Lock()

        def worker(uid):
            try:
                s.book("show1", ["A1"], uid)
                with rlock:
                    results.append("ok")
            except SeatUnavailable:
                pass

        threads = [threading.Thread(target=worker, args=(f"u{i}",)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(results.count("ok"), 1)     # exactly one booking succeeded
        self.assertEqual(s.available_seats("show1"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
