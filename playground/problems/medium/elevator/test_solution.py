"""Runnable tests for the Elevator. Write solution.py first."""
import unittest

try:
    from solution import Elevator
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Elevator = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


def run_until_idle(elev, max_steps=100):
    """Step until idle; return the ordered list of floors serviced (targets removed)."""
    serviced = []
    for _ in range(max_steps):
        before = set(elev.targets)
        elev.step()
        removed = before - set(elev.targets)
        for f in removed:
            serviced.append(f)
        if elev.direction == "IDLE" and not elev.targets:
            break
    return serviced


class TestLook(unittest.TestCase):
    def test_go_up_and_service(self):
        e = Elevator(current_floor=0, max_floor=10)
        e.request_floor(1)
        e.request_floor(3)
        serviced = run_until_idle(e)
        self.assertEqual(serviced, [1, 3])
        self.assertEqual(e.current_floor, 3)
        self.assertEqual(e.direction, "IDLE")

    def test_go_down_and_service(self):
        e = Elevator(current_floor=5, max_floor=10)
        e.request_floor(2)
        serviced = run_until_idle(e)
        self.assertEqual(serviced, [2])
        self.assertEqual(e.current_floor, 2)
        self.assertEqual(e.direction, "IDLE")

    def test_look_reverses_after_finishing_a_direction(self):
        # From floor 3, one target below (1) is nearer than one above (6): serve 1 then reverse to 6.
        e = Elevator(current_floor=3, max_floor=10)
        e.request_floor(6)
        e.request_floor(1)
        serviced = run_until_idle(e)
        self.assertEqual(serviced, [1, 6])   # down first (nearer), then reverse up
        self.assertEqual(e.current_floor, 6)
        self.assertEqual(e.direction, "IDLE")

    def test_request_current_floor_serviced_next_step(self):
        e = Elevator(current_floor=4, max_floor=10)
        e.request_floor(4)
        e.step()                       # services floor 4 in place
        self.assertNotIn(4, e.targets)
        self.assertEqual(e.current_floor, 4)

    def test_starts_idle(self):
        e = Elevator()
        self.assertEqual(e.direction, "IDLE")
        e.step()                       # nothing to do
        self.assertEqual(e.direction, "IDLE")

    def test_direction_is_up_while_climbing(self):
        e = Elevator(current_floor=0, max_floor=10)
        e.request_floor(5)
        e.step()
        self.assertEqual(e.direction, "UP")
        self.assertEqual(e.current_floor, 1)


class TestValidation(unittest.TestCase):
    def test_out_of_range_request_raises(self):
        e = Elevator(current_floor=0, min_floor=0, max_floor=10)
        with self.assertRaises(ValueError):
            e.request_floor(11)
        with self.assertRaises(ValueError):
            e.request_floor(-1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
