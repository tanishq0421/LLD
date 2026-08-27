"""Runnable tests for the Logging Framework. Write solution.py first."""
import unittest

try:
    from solution import Logger
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Logger = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestLevelFiltering(unittest.TestCase):
    def test_below_min_is_dropped(self):
        log = Logger(min_level="INFO")
        self.assertEqual(log.debug("noise"), [])

    def test_at_min_is_emitted(self):
        log = Logger(min_level="INFO")
        self.assertEqual(log.info("started"), ["INFO: started"])

    def test_above_min_is_emitted(self):
        log = Logger(min_level="INFO")
        self.assertEqual(log.error("boom"), ["ERROR: boom"])

    def test_warning_threshold(self):
        log = Logger(min_level="WARNING")
        self.assertEqual(log.debug("a"), [])
        self.assertEqual(log.info("b"), [])
        self.assertEqual(log.warning("c"), ["WARNING: c"])
        self.assertEqual(log.error("d"), ["ERROR: d"])

    def test_debug_min_emits_everything(self):
        log = Logger(min_level="DEBUG")
        self.assertEqual(log.debug("x"), ["DEBUG: x"])
        self.assertEqual(log.info("y"), ["INFO: y"])

    def test_generic_log_method(self):
        log = Logger(min_level="INFO")
        self.assertEqual(log.log("ERROR", "via generic"), ["ERROR: via generic"])
        self.assertEqual(log.log("DEBUG", "via generic"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
