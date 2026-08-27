"""
Test contract for Splitwise.

Your `solution.py` must define `Splitwise` and a `SplitError` exception.

Split types are the strings "EQUAL", "EXACT", "PERCENT".

    class Splitwise:
        def add_user(self, user_id: str, name: str = "", email: str = "", mobile: str = "") -> None:
            ...

        def add_expense(self, paid_by: str, amount: float, participants: list,
                        split_type: str, values: list = None) -> None:
            # participants: list of user_ids sharing the cost (may or may not include paid_by).
            # EQUAL  : split `amount` equally among participants; `values` ignored.
            # EXACT  : `values[i]` is participant[i]'s exact share; sum(values) must == amount.
            # PERCENT: `values[i]` is participant[i]'s percentage; sum(values) must == 100.
            # Raise SplitError if a user is unknown, values length mismatches, or sums are wrong.
            # Each participant (other than paid_by) then owes paid_by their share. Balances NET
            # across calls.

        def get_balance(self, a: str, b: str) -> float:
            # Net amount `a` owes `b`, rounded to 2 decimals.
            # Positive => a owes b.  Negative => b owes a.  0.0 => settled.

        def get_balances(self, user_id: str) -> dict:
            # {other_user_id: amount} for every non-zero balance involving user_id, where
            # amount > 0 means user_id owes them, amount < 0 means they owe user_id.

Round monetary values to 2 decimals.
"""
