"""Runnable tests for the Job Scheduler. Write solution.py first."""
import unittest

try:
    from solution import Scheduler, CycleError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Scheduler = CycleError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


def assert_topo_valid(test, order, deps_map):
    """Every dependency must appear before the job that needs it."""
    pos = {job: i for i, job in enumerate(order)}
    test.assertEqual(set(order), set(deps_map), "order must contain every job exactly once")
    test.assertEqual(len(order), len(set(order)), "no duplicates in order")
    for job, deps in deps_map.items():
        for d in deps:
            test.assertLess(pos[d], pos[job], f"{d} must come before {job}")


class TestOrder(unittest.TestCase):
    def test_linear_chain(self):
        s = Scheduler()
        s.add_job("A")
        s.add_job("B", ["A"])
        s.add_job("C", ["B"])
        self.assertEqual(s.get_execution_order(), ["A", "B", "C"])

    def test_diamond(self):
        s = Scheduler()
        deps = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
        for j, d in deps.items():
            s.add_job(j, d)
        order = s.get_execution_order()
        assert_topo_valid(self, order, deps)

    def test_deterministic_tie_break(self):
        s = Scheduler()
        # three independent roots -> sorted by id
        for j in ("C", "A", "B"):
            s.add_job(j)
        self.assertEqual(s.get_execution_order(), ["A", "B", "C"])

    def test_forward_declared_dependency(self):
        s = Scheduler()
        s.add_job("B", ["A"])     # declare B before A exists
        s.add_job("A")
        self.assertEqual(s.get_execution_order(), ["A", "B"])

    def test_cycle_detected(self):
        s = Scheduler()
        s.add_job("A", ["B"])
        s.add_job("B", ["A"])
        with self.assertRaises(CycleError):
            s.get_execution_order()

    def test_unknown_dependency(self):
        s = Scheduler()
        s.add_job("A", ["ghost"])
        with self.assertRaises(KeyError):
            s.get_execution_order()

    def test_duplicate_job(self):
        s = Scheduler()
        s.add_job("A")
        with self.assertRaises(ValueError):
            s.add_job("A")


class TestReady(unittest.TestCase):
    def test_initial_ready_are_rootless(self):
        s = Scheduler()
        s.add_job("A")
        s.add_job("B", ["A"])
        s.add_job("C")
        self.assertEqual(s.ready(), ["A", "C"])

    def test_mark_done_unlocks_dependents(self):
        s = Scheduler()
        s.add_job("A")
        s.add_job("B", ["A"])
        self.assertEqual(s.ready(), ["A"])
        s.mark_done("A")
        self.assertEqual(s.ready(), ["B"])   # A done -> B ready, A no longer ready

    def test_all_deps_needed(self):
        s = Scheduler()
        s.add_job("A")
        s.add_job("B")
        s.add_job("C", ["A", "B"])
        s.mark_done("A")
        self.assertEqual(s.ready(), ["B"])   # C still blocked on B
        s.mark_done("B")
        self.assertEqual(s.ready(), ["C"])

    def test_mark_done_unknown(self):
        s = Scheduler()
        with self.assertRaises(KeyError):
            s.mark_done("nope")


if __name__ == "__main__":
    unittest.main(verbosity=2)
