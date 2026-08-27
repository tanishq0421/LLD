"""Runnable tests for the ATM. Write solution.py first."""
import unittest

try:
    from solution import ATM, ATMError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    ATM = ATMError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


def atm(cash=None):
    cash = cash or {2000: 5, 500: 5, 100: 5}
    accounts = {"C1": {"pin": "1234", "balance": 10000}}
    return ATM(cash=cash, accounts=accounts)


class TestStateMachine(unittest.TestCase):
    def test_starts_idle(self):
        self.assertEqual(atm().state, "IDLE")

    def test_insert_then_authenticate(self):
        a = atm()
        a.insert_card("C1")
        self.assertEqual(a.state, "HAS_CARD")
        a.enter_pin("1234")
        self.assertEqual(a.state, "AUTHENTICATED")

    def test_wrong_pin_stays_has_card(self):
        a = atm()
        a.insert_card("C1")
        with self.assertRaises(ATMError):
            a.enter_pin("0000")
        self.assertEqual(a.state, "HAS_CARD")

    def test_withdraw_requires_auth(self):
        a = atm()
        a.insert_card("C1")
        with self.assertRaises(ATMError):
            a.withdraw(100)

    def test_unknown_card(self):
        a = atm()
        with self.assertRaises(ATMError):
            a.insert_card("NOPE")

    def test_eject_returns_to_idle(self):
        a = atm()
        a.insert_card("C1")
        a.enter_pin("1234")
        a.eject_card()
        self.assertEqual(a.state, "IDLE")


class TestDispensing(unittest.TestCase):
    def setUp(self):
        self.a = atm()
        self.a.insert_card("C1")
        self.a.enter_pin("1234")

    def test_mixed_denominations(self):
        out = self.a.withdraw(2600)
        self.assertEqual(out, {2000: 1, 500: 1, 100: 1})
        self.assertEqual(self.a.balance(), 7400)

    def test_greedy_breakdown(self):
        self.assertEqual(self.a.withdraw(3000), {2000: 1, 500: 2})

    def test_non_dispensable_amount_rejected(self):
        with self.assertRaises(ATMError):
            self.a.withdraw(250)          # not composable from 2000/500/100
        self.assertEqual(self.a.balance(), 10000)  # unchanged

    def test_insufficient_funds(self):
        with self.assertRaises(ATMError):
            self.a.withdraw(999999)

    def test_insufficient_notes(self):
        a = atm(cash={2000: 0, 500: 1, 100: 0})
        a.insert_card("C1"); a.enter_pin("1234")
        self.assertEqual(a.withdraw(500), {500: 1})
        with self.assertRaises(ATMError):
            a.withdraw(600)               # no 100s available -> cannot dispense

    def test_notes_are_deducted(self):
        self.a.withdraw(2000)             # takes one 2000 note
        # only 4 x 2000 left now: withdrawing 5*2000 worth from 2000s should fail to compose 10000
        # (4*2000=8000 in 2000s; remainder 2000 must come from 500s: 4 available = 2000) -> ok actually
        out = self.a.withdraw(8000)       # 4x2000 + 0... needs 8000: 4*2000 = 8000
        self.assertEqual(out, {2000: 4})


if __name__ == "__main__":
    unittest.main(verbosity=2)
