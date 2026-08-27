"""
Test contract for the Vending Machine.

Your `solution.py` must define `VendingMachine` and a `VendingError` exception:

    class VendingMachine:
        def __init__(self): ...

        def add_product(self, code: str, name: str, price: int, quantity: int) -> None:
            # Stock (or restock) a product slot identified by `code`.

        def insert_coin(self, denomination: int) -> None:
            # Add to the current balance. (You may validate accepted denominations.)

        def select(self, code: str) -> None:
            # Choose a product. Raise VendingError if the code is unknown or out of stock.

        def dispense(self) -> tuple:
            # Require a current selection and balance >= price.
            # Return (name: str, change: int). Decrement inventory. Reset to idle (balance 0).
            # Raise VendingError if nothing is selected or the balance is insufficient.

        def refund(self) -> int:
            # Cancel the interaction, clear any selection, and return the full inserted balance.

        @property
        def balance(self) -> int:
            # Coins inserted since the last dispense/refund.

        @property
        def state(self) -> str:
            # A human-readable state name, e.g. "IDLE" or "HAS_SELECTION".
            # (Tests only check IDLE vs non-IDLE transitions loosely — exact names are yours,
            #  but "IDLE" must be the name of the no-selection state.)

Everything else — how you represent states, products, and change — is your design.
"""
