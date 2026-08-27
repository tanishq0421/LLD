"""Runnable tests for the Ride-Hailing service. Write solution.py first."""
import unittest

try:
    from solution import RideService, NoDriverAvailable, InvalidTrip
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    RideService = NoDriverAvailable = InvalidTrip = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestMatching(unittest.TestCase):
    def test_matches_nearest_driver(self):
        s = RideService()
        s.register_driver("d1", 0, 0)
        s.register_driver("d2", 10, 10)
        trip = s.request_ride("r1", 1, 1)   # d1 (dist 2) closer than d2 (dist 18)
        self.assertEqual(s.get_driver(trip), "d1")

    def test_busy_driver_not_rematched(self):
        s = RideService()
        s.register_driver("d1", 0, 0)
        s.register_driver("d2", 5, 5)
        t1 = s.request_ride("r1", 0, 0)     # takes d1
        t2 = s.request_ride("r2", 0, 0)     # d1 busy -> d2
        self.assertEqual(s.get_driver(t1), "d1")
        self.assertEqual(s.get_driver(t2), "d2")

    def test_no_driver_available(self):
        s = RideService()
        s.register_driver("d1", 0, 0)
        s.request_ride("r1", 0, 0)
        with self.assertRaises(NoDriverAvailable):
            s.request_ride("r2", 0, 0)


class TestLifecycle(unittest.TestCase):
    def setUp(self):
        self.s = RideService()
        self.s.register_driver("d1", 0, 0)

    def test_full_happy_path(self):
        t = self.s.request_ride("r1", 0, 0)
        self.assertEqual(self.s.trip_status(t), "ASSIGNED")
        self.s.start_trip(t)
        self.assertEqual(self.s.trip_status(t), "ONGOING")
        fare = self.s.end_trip(t, 3, 4)     # Manhattan 7 -> 50 + 70 = 120
        self.assertEqual(fare, 120)
        self.assertEqual(self.s.trip_status(t), "COMPLETED")

    def test_driver_freed_after_trip(self):
        t = self.s.request_ride("r1", 0, 0)
        self.s.start_trip(t)
        self.s.end_trip(t, 2, 2)
        # d1 free again (now at drop) -> new request matches d1
        t2 = self.s.request_ride("r2", 2, 2)
        self.assertEqual(self.s.get_driver(t2), "d1")

    def test_cancel_frees_driver(self):
        t = self.s.request_ride("r1", 0, 0)
        self.s.cancel_trip(t)
        self.assertEqual(self.s.trip_status(t), "CANCELLED")
        t2 = self.s.request_ride("r2", 0, 0)
        self.assertEqual(self.s.get_driver(t2), "d1")

    def test_custom_pricing(self):
        s = RideService(pricing=lambda d: 5 * d)
        s.register_driver("d1", 0, 0)
        t = s.request_ride("r1", 0, 0)
        s.start_trip(t)
        self.assertEqual(s.end_trip(t, 0, 4), 20)   # dist 4 -> 20


class TestInvalidTransitions(unittest.TestCase):
    def setUp(self):
        self.s = RideService()
        self.s.register_driver("d1", 0, 0)

    def test_start_non_assigned(self):
        t = self.s.request_ride("r1", 0, 0)
        self.s.start_trip(t)
        with self.assertRaises(InvalidTrip):
            self.s.start_trip(t)           # already ONGOING

    def test_end_non_ongoing(self):
        t = self.s.request_ride("r1", 0, 0)
        with self.assertRaises(InvalidTrip):
            self.s.end_trip(t, 1, 1)       # not started yet

    def test_cancel_completed(self):
        t = self.s.request_ride("r1", 0, 0)
        self.s.start_trip(t)
        self.s.end_trip(t, 1, 1)
        with self.assertRaises(InvalidTrip):
            self.s.cancel_trip(t)

    def test_unknown_trip(self):
        with self.assertRaises(KeyError):
            self.s.trip_status("nope")


@unittest.skip("Follow-up: concurrency. Remove this skip once matching is thread-safe.")
class TestConcurrency(unittest.TestCase):
    def test_one_driver_not_double_assigned(self):
        import threading
        s = RideService()
        s.register_driver("d1", 0, 0)        # single driver
        assigned = []
        rlock = threading.Lock()

        def worker(rid):
            try:
                t = s.request_ride(rid, 0, 0)
                with rlock:
                    assigned.append(t)
            except NoDriverAvailable:
                pass

        threads = [threading.Thread(target=worker, args=(f"r{i}",)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(assigned), 1)   # exactly one rider got the driver


if __name__ == "__main__":
    unittest.main(verbosity=2)
