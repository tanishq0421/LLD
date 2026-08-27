"""Runnable tests for Splitwise. Write solution.py first."""
import unittest

try:
    from solution import Splitwise, SplitError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Splitwise = SplitError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


def sw():
    s = Splitwise()
    for u in ("u1", "u2", "u3", "u4"):
        s.add_user(u, name=u.upper())
    return s


class TestEqual(unittest.TestCase):
    def test_equal_split(self):
        s = sw()
        s.add_expense("u1", 300, ["u1", "u2", "u3"], "EQUAL")
        self.assertEqual(s.get_balance("u2", "u1"), 100.0)
        self.assertEqual(s.get_balance("u3", "u1"), 100.0)
        self.assertEqual(s.get_balance("u1", "u2"), -100.0)  # symmetric
        self.assertEqual(s.get_balance("u1", "u1"), 0.0)

    def test_payer_not_in_group(self):
        s = sw()
        s.add_expense("u1", 200, ["u2", "u3"], "EQUAL")  # u1 paid for u2,u3 only
        self.assertEqual(s.get_balance("u2", "u1"), 100.0)
        self.assertEqual(s.get_balance("u3", "u1"), 100.0)


class TestExact(unittest.TestCase):
    def test_exact_split(self):
        s = sw()
        s.add_expense("u1", 300, ["u1", "u2", "u3"], "EXACT", [0, 100, 200])
        self.assertEqual(s.get_balance("u2", "u1"), 100.0)
        self.assertEqual(s.get_balance("u3", "u1"), 200.0)

    def test_exact_must_sum_to_amount(self):
        s = sw()
        with self.assertRaises(SplitError):
            s.add_expense("u1", 300, ["u1", "u2", "u3"], "EXACT", [0, 100, 100])


class TestPercent(unittest.TestCase):
    def test_percent_split(self):
        s = sw()
        s.add_expense("u1", 1000, ["u1", "u2", "u3"], "PERCENT", [20, 30, 50])
        self.assertEqual(s.get_balance("u2", "u1"), 300.0)
        self.assertEqual(s.get_balance("u3", "u1"), 500.0)

    def test_percent_must_sum_to_100(self):
        s = sw()
        with self.assertRaises(SplitError):
            s.add_expense("u1", 1000, ["u1", "u2", "u3"], "PERCENT", [20, 30, 40])


class TestValidationAndNetting(unittest.TestCase):
    def test_unknown_user_raises(self):
        s = sw()
        with self.assertRaises(SplitError):
            s.add_expense("u1", 100, ["u1", "ghost"], "EQUAL")

    def test_values_length_mismatch(self):
        s = sw()
        with self.assertRaises(SplitError):
            s.add_expense("u1", 100, ["u1", "u2"], "EXACT", [100])

    def test_balances_net_across_expenses(self):
        s = sw()
        s.add_expense("u1", 100, ["u1", "u2"], "EQUAL")  # u2 owes u1 50
        s.add_expense("u2", 20, ["u1", "u2"], "EQUAL")   # u1 owes u2 10 -> net u2 owes u1 40
        self.assertEqual(s.get_balance("u2", "u1"), 40.0)
        self.assertEqual(s.get_balance("u1", "u2"), -40.0)

    def test_get_balances_only_nonzero(self):
        s = sw()
        s.add_expense("u1", 100, ["u1", "u2"], "EQUAL")  # u2 owes u1 50
        balances = s.get_balances("u2")
        self.assertEqual(balances, {"u1": 50.0})
        self.assertEqual(s.get_balances("u3"), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
