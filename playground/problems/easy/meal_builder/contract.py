"""
Test contract for the Meal Builder (Builder).

Your `solution.py` must define `MealBuilder`, `Meal`, and a `BuildError` exception.

    class MealBuilder:
        def __init__(self, name: str): ...

        def add_main(self, item: str, price: float) -> "MealBuilder":   # returns self (chainable)
        def add_side(self, item: str, price: float) -> "MealBuilder":   # returns self
        def add_drink(self, item: str, price: float) -> "MealBuilder":  # returns self
        def set_size(self, size: str) -> "MealBuilder":                 # returns self

        def build(self) -> "Meal":
            # Validate at least one main was added, else raise BuildError. Return a finished Meal.

    class Meal:
        @property
        def name(self) -> str: ...
        @property
        def size(self) -> str: ...            # default "regular" if set_size was never called
        @property
        def items(self) -> list: ...          # item names in the order they were added
        @property
        def total_price(self) -> float: ...   # sum of all item prices

The finished Meal should not require further mutation. Implement with the Builder pattern.
"""
