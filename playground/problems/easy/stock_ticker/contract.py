"""
Test contract for the Stock Price Ticker (Observer).

Your `solution.py` must define `Stock`. An "observer" is any object with a method
`update(symbol: str, old_price: float, new_price: float) -> None`.

    class Stock:
        def __init__(self, symbol: str, price: float): ...

        @property
        def price(self) -> float: ...

        @property
        def symbol(self) -> str: ...

        def subscribe(self, observer) -> None:
            # Register an observer. Idempotent: subscribing the same observer twice must NOT
            # cause duplicate notifications.

        def unsubscribe(self, observer) -> None:
            # Stop notifying this observer. Unknown observer -> no-op.

        def set_price(self, new_price: float) -> None:
            # Update the price. If (and only if) the value changed, notify every observer via
            # observer.update(symbol, old_price, new_price).

Implement the notification with the Observer pattern (subject depends on the observer interface,
not on concrete observer classes).
"""
