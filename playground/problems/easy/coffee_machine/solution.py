"""
COFFEE MACHINE — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Start from a base drink; wrap it with zero or more add-ons, each adding its own cost and label."
    nouns -> CoffeeShop, Beverage (base + decorated), add-on (milk/sugar/caramel)
    verbs -> base (create), add (wrap with one more add-on), cost, description
  Base drink names and add-on names are closed value sets backed by price tables (data), not
  class hierarchies of their own — the VARIATION that needs real classes is "how many add-ons,
  in what combination", which is unbounded and exactly what Decorator is for (STEP 3).

STEP 2 — ENTITIES & RELATIONSHIPS
  CoffeeShop ───▶ Beverage        ASSOCIATION: the shop is a FACTORY that creates/wraps beverages;
                                  it doesn't own or hold onto them after returning one.
  AddonBeverage ◆──── Beverage    COMPOSITION: each decorator wraps exactly one inner beverage and
                                  that inner object's lifetime is tied to the wrapper holding it.
  NO inheritance tree like "EspressoWithMilk", "EspressoWithMilkAndSugar" — that would need a new
  class per COMBINATION of add-ons (combinatorial explosion). Add-ons differ by which extra cost/
  label they layer on, which is exactly behaviour composition, not a data difference to subclass.

STEP 3 — PATTERN? (what varies?)
  This is the textbook home for DECORATOR: the base object (a plain espresso/latte/cappuccino) and
  each add-on share the same interface (cost(), description()), and add-ons wrap a beverage to
  extend its cost/description WITHOUT modifying the wrapped object or needing one subclass per
  combination. `add()` returns a NEW wrapping object each time, so repeated/ordered add-ons and an
  unmutated original beverage fall out of the design for free — no special-casing needed.

STEP 4 — SOLID
  SRP  Each decorator knows only its own add-on's price/label; it delegates everything else to the
       beverage it wraps (cost() = inner.cost() + my price).
  OCP  A brand-new add-on (e.g. "vanilla") is a new price-table entry, not a change to existing
       decorator classes. A brand-new BASE drink is likewise just a new BASE_PRICES entry.
  LSP  Every decorator honors the same Beverage interface as a plain base drink, so add() can wrap
       a beverage that is itself already-decorated (add(add(base, "milk"), "sugar")) transparently.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (object flow / a run-through) ─────────────────────
#   shop = CoffeeShop()
#   b = shop.base("latte")            # BaseBeverage("latte", 3.0) -> cost 3.0, desc "Latte"
#   b = shop.add(b, "milk")           # wraps b -> cost 3.0+0.5=3.5, desc "Latte, Milk"
#   b = shop.add(b, "sugar")          # wraps AGAIN -> cost 3.5+0.25=3.75, desc "Latte, Milk, Sugar"
#   b.cost()                          # 3.75          (each layer adds its own price on the way out)
#   b.description()                  # "Latte, Milk, Sugar"
#   # The ORIGINAL object from shop.base("latte") is untouched — each add() call built a brand new
#   # wrapper object around whatever was passed in; nothing was mutated in place.
#   # Flow: caller -> CoffeeShop.base (build the innermost object) -> repeated CoffeeShop.add (each
#   #        wraps the previous result in one more decorator) -> cost()/description() recurse
#   #        outside-in through every layer down to the base and sum/concatenate back up.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# BASE_PRICES = {"espresso": 2.0, "latte": 3.0, "cappuccino": 3.5}
# ADDON_PRICES = {"milk": 0.5, "sugar": 0.25, "caramel": 0.75}


# class MenuError(Exception):
#     pass


# class Beverage:
#     # LOGIC: shared interface every base drink and every decorator must implement. Not strictly
#     # required in Python (duck typing would work without it), but naming it makes the Decorator
#     # contract explicit: "anything with cost()+description() can be wrapped or returned".
#     def cost(self):
#         raise NotImplementedError

#     def description(self):
#         raise NotImplementedError


# class BaseBeverage(Beverage):
#     # The innermost object in the decorator chain — a plain drink with no add-ons yet.
#     def __init__(self, name, price):
#         self._name = name
#         self._price = price

#     def cost(self):
#         return self._price

#     def description(self):
#         return self._name.title()          # "espresso" -> "Espresso"


# class AddonDecorator(Beverage):
#     # LOGIC: wraps an existing beverage (base OR another decorator) and adds exactly one add-on's
#     # cost/label on top. Because it stores `_beverage` (not mutates it), the original object passed
#     # in is left completely unchanged — decorating always produces a NEW outer object.
#     def __init__(self, beverage, addon_name, addon_price):
#         self._beverage = beverage
#         self._addon_name = addon_name
#         self._addon_price = addon_price

#     def cost(self):
#         # recurse inward: my price + whatever everything I wrap already costs
#         return self._beverage.cost() + self._addon_price

#     def description(self):
#         # recurse inward then append: "<inner description>, <My Addon>"
#         return f"{self._beverage.description()}, {self._addon_name.title()}"


# class CoffeeShop:
#     def base(self, name):
#         if name not in BASE_PRICES:
#             raise MenuError(f"unknown base drink: {name}")
#         return BaseBeverage(name, BASE_PRICES[name])

#     def add(self, beverage, addon):
#         if addon not in ADDON_PRICES:
#             raise MenuError(f"unknown add-on: {addon}")
#         # LOGIC: `beverage` may already be an AddonDecorator from a previous add() call — that's
#         # fine, we just wrap it again. Repeated calls stack decorators like layers of an onion.
#         return AddonDecorator(beverage, addon, ADDON_PRICES[addon])
