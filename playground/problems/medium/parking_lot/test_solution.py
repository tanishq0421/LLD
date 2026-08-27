"""Runnable tests for the Parking Lot. Write solution.py first."""
import unittest

try:
    from solution import ParkingLot, ParkingFull, InvalidTicket
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    ParkingLot = ParkingFull = InvalidTicket = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class Clock:
    """Controllable clock the tests advance manually (seconds)."""
    def __init__(self, t=0):
        self.t = t
    def __call__(self):
        return self.t


def small_lot(clock=None):
    lot = ParkingLot(clock=clock)
    lot.add_spot("S1", "SMALL")
    lot.add_spot("M1", "MEDIUM")
    lot.add_spot("L1", "LARGE")
    return lot


class TestParking(unittest.TestCase):
    def test_park_returns_ticket_and_decrements(self):
        lot = small_lot()
        self.assertEqual(lot.available_count(), 3)
        t = lot.park("CAR-1", "CAR")
        self.assertIsNotNone(t)
        self.assertEqual(lot.available_count(), 2)

    def test_best_fit_motorcycle_takes_small(self):
        lot = small_lot()
        lot.park("BIKE-1", "MOTORCYCLE")   # should take SMALL, not MEDIUM/LARGE
        self.assertEqual(lot.available_count("SMALL"), 0)
        self.assertEqual(lot.available_count("MEDIUM"), 1)
        self.assertEqual(lot.available_count("LARGE"), 1)

    def test_car_cannot_use_small(self):
        lot = ParkingLot()
        lot.add_spot("S1", "SMALL")
        with self.assertRaises(ParkingFull):
            lot.park("CAR-1", "CAR")

    def test_truck_needs_large(self):
        lot = ParkingLot()
        lot.add_spot("S1", "SMALL")
        lot.add_spot("M1", "MEDIUM")
        with self.assertRaises(ParkingFull):
            lot.park("TRUCK-1", "TRUCK")
        lot.add_spot("L1", "LARGE")
        self.assertIsNotNone(lot.park("TRUCK-1", "TRUCK"))

    def test_full_lot_raises(self):
        lot = ParkingLot()
        lot.add_spot("L1", "LARGE")
        lot.park("T1", "TRUCK")
        with self.assertRaises(ParkingFull):
            lot.park("T2", "TRUCK")

    def test_motorcycle_overflows_to_larger_when_small_full(self):
        lot = ParkingLot()
        lot.add_spot("S1", "SMALL")
        lot.add_spot("M1", "MEDIUM")
        lot.park("B1", "MOTORCYCLE")  # takes SMALL
        lot.park("B2", "MOTORCYCLE")  # SMALL full -> overflow to MEDIUM
        self.assertEqual(lot.available_count(), 0)


class TestUnparkAndFees(unittest.TestCase):
    def test_unpark_frees_spot(self):
        lot = small_lot()
        t = lot.park("CAR-1", "CAR")
        self.assertEqual(lot.available_count(), 2)
        lot.unpark(t)
        self.assertEqual(lot.available_count(), 3)

    def test_fee_minimum_one_hour(self):
        clk = Clock(0)
        lot = small_lot(clock=clk)
        t = lot.park("CAR-1", "CAR")   # entry at 0
        clk.t = 60                      # 1 minute later
        self.assertEqual(lot.unpark(t), 20)  # rounds up to 1 hour * 20

    def test_fee_duration_rounds_up(self):
        clk = Clock(0)
        lot = small_lot(clock=clk)
        t = lot.park("TRUCK-1", "TRUCK")  # LARGE, rate 30
        clk.t = 3600 * 2 + 1              # just over 2 hours -> 3 hours
        self.assertEqual(lot.unpark(t), 90)

    def test_invalid_ticket_raises(self):
        lot = small_lot()
        with self.assertRaises(InvalidTicket):
            lot.unpark("does-not-exist")

    def test_double_unpark_raises(self):
        lot = small_lot()
        t = lot.park("CAR-1", "CAR")
        lot.unpark(t)
        with self.assertRaises(InvalidTicket):
            lot.unpark(t)


if __name__ == "__main__":
    unittest.main(verbosity=2)
