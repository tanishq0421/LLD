"""
Test contract for the Discount / Coupon Engine (Strategy + Chain of Responsibility).

Your `solution.py` must define `Cart` and `DiscountEngine`.

A "rule" is a callable: rule(cart, running_total) -> new_total. (Model it as a Strategy — a function
or a class with __call__. The engine chains rules in the order they were added.)

    class Cart:
        def add_item(self, name: str, price: float, qty: int = 1) -> None: ...
        def subtotal(self) -> float:
            # Sum of price * qty over all items.

    class DiscountEngine:
        def add_rule(self, rule) -> None:
            # Append a rule (callable) to the chain.

        def total(self, cart: "Cart") -> float:
            # Start from cart.subtotal(), fold each rule in order (t = rule(cart, t)),
            # floor at 0, round to 2 decimals.

        # Built-in rule builders (each RETURNS a rule callable):
        @staticmethod
        def percentage(pct: float): ...          # t -> t * (1 - pct/100)
        @staticmethod
        def flat(amount: float): ...             # t -> max(0, t - amount)
        @staticmethod
        def threshold(min_subtotal: float, amount: float): ...
            # if cart.subtotal() >= min_subtotal: t -> max(0, t - amount) else t unchanged
"""
