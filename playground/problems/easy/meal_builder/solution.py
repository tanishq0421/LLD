"""
MEAL BUILDER — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Assemble a meal from a main, optional sides/drinks and a size, then finalize it."
    nouns -> MealBuilder (accumulator), Meal (finished value object)
    verbs -> add_main, add_side, add_drink, set_size -> build
  Item "kind" (main/side/drink) is only ever used to enforce "at least one main" — not exposed
  or branched on later, so it doesn't need its own class or enum; a boolean flag is enough.

STEP 2 — ENTITIES & RELATIONSHIPS
  MealBuilder ┄┄▶ Meal        CREATES (not composition): build() constructs ONE Meal from the
                              builder's accumulated state and returns it; the builder can be
                              discarded or reused for a next meal afterward.
  Meal ◆──── items            COMPOSITION: the finished Meal owns its item list outright — once
                              built it is a frozen snapshot, not a live view into the builder.
  NO inheritance for Main/Side/Drink: they differ only by WHICH LIST they land in, not by
  behaviour — a MainSubclass/SideSubclass hierarchy would be pure ceremony.

STEP 3 — PATTERN? (what varies?)
  WHAT varies: which optional pieces get added, in what combination, before the object is
  considered "done". Builder is the textbook fit: a fluent interface (each add_* returns self)
  accumulates state step by step, and build() is the single gate where validation happens and an
  immutable result is produced — the caller never sees a half-constructed Meal.

STEP 4 — SOLID
  SRP   MealBuilder = accumulation + validation. Meal = a read-only finished value (name, size,
        items, total) with no behaviour of its own.
  OCP   Adding a new optional category (e.g. add_dessert) means one new method following the
        same shape — build()'s "must have a main" rule doesn't change.
  ENCAPSULATION  build() copies the accumulated items into the Meal rather than handing the
        builder's own list over, so mutating the builder afterward can't corrupt an already-built
        Meal.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (object flow / a run-through) ─────────────────────
#   b = MealBuilder("Combo")                  # start accumulating for a meal named "Combo"
#   b.add_main("Burger", 5.0)                 # returns b (chainable); has_main -> True
#   b.add_side("Fries", 2.0).add_drink("Coke", 1.5)   # chain further; items so far: 3
#   b.set_size("large")                       # optional; would default to "regular" if skipped
#   meal = b.build()                          # validate has_main (True) -> snapshot into a Meal
#   meal.items                                # ["Burger", "Fries", "Coke"]  (insertion order)
#   meal.total_price                          # 8.5  (5.0 + 2.0 + 1.5)
#   meal.size                                 # "large"
#   MealBuilder("Empty").add_side("Fries", 2.0).build()   # no main added -> raises BuildError
#   # Flow: caller chains add_*/set_size on the builder -> build() validates -> returns a frozen Meal.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# class BuildError(Exception):
#     pass


# class Meal:
#     # LOGIC: Meal is a plain, read-only value object — built once by MealBuilder.build(), never
#     # mutated afterward. Only properties, no setters, keeps it safe to hand out to callers.
#     def __init__(self, name, size, items, total_price):
#         self._name = name
#         self._size = size
#         self._items = items          # already a fresh list, copied by the builder before this call
#         self._total_price = total_price

#     @property
#     def name(self):
#         return self._name

#     @property
#     def size(self):
#         return self._size

#     @property
#     def items(self):
#         return self._items

#     @property
#     def total_price(self):
#         return self._total_price


# class MealBuilder:
#     def __init__(self, name):
#         self._name = name
#         self._size = "regular"       # default per contract: unset size -> "regular"
#         self._items = []             # [(item_name, price), ...] in the order they were added
#         self._has_main = False       # LOGIC: tracked separately so build() validates in O(1)
#                                       # instead of re-scanning _items for "was a main ever added?"

#     def add_main(self, item, price):
#         self._items.append((item, price))
#         self._has_main = True
#         return self                  # CHAINABLE: every add_*/set_* returns self (fluent Builder)

#     def add_side(self, item, price):
#         self._items.append((item, price))
#         return self

#     def add_drink(self, item, price):
#         self._items.append((item, price))
#         return self

#     def set_size(self, size):
#         self._size = size
#         return self

#     def build(self):
#         if not self._has_main:
#             raise BuildError("a meal must include at least one main")
#         # LOGIC: derive items/total from the accumulated (name, price) pairs.
#         names = [name for name, _price in self._items]
#         total = sum(price for _name, price in self._items)
#         return Meal(self._name, self._size, names, total)
