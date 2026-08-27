"""
Test contract for the Coffee Machine (Decorator).

Your `solution.py` must define `CoffeeShop` and a `MenuError` exception. A "beverage" is any object
your design returns that supports `.cost() -> float` and `.description() -> str`.

    BASE PRICES  = {"espresso": 2.0, "latte": 3.0, "cappuccino": 3.5}
    ADDON PRICES = {"milk": 0.5, "sugar": 0.25, "caramel": 0.75}

    class CoffeeShop:
        def base(self, name: str):
            # Return a new beverage for a known base. Raise MenuError if unknown.
            # beverage.cost() == base price; beverage.description() == "Espresso" (title-cased name).

        def add(self, beverage, addon: str):
            # Return a beverage decorated with `addon` (repeats allowed). Raise MenuError if unknown.
            # new.cost() == beverage.cost() + addon price
            # new.description() == beverage.description() + ", " + Addon (title-cased)

Description uses title-case names, add-ons appended in the order added, comma-space separated,
e.g. "Espresso, Milk, Sugar". Implement the composition with the Decorator pattern.
"""

BASE_PRICES = {"espresso": 2.0, "latte": 3.0, "cappuccino": 3.5}
ADDON_PRICES = {"milk": 0.5, "sugar": 0.25, "caramel": 0.75}
