"""
VENDING MACHINE — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "A buyer inserts coins, selects a stocked product, and the machine dispenses it plus change."
    nouns -> VendingMachine, Product (code/name/price/qty), Coin/balance
    verbs -> add_product(stock), insert_coin, select, dispense, refund
  Product codes and coin denominations are DATA, not classes. "State" (IDLE / HAS_SELECTION) is a
  closed value set -> could be an Enum, but a plain string is enough here (contract wants a string).

STEP 2 — ENTITIES & RELATIONSHIPS
  VendingMachine ◆──── Product   COMPOSITION: the machine owns its product slots (added via
                                 add_product, die with the machine).
  VendingMachine ───▶ selection  ASSOCIATION: "currently selected code" is just a reference
                                 (a string) into the product map, not an owned object.
  NO inheritance for product types — a product is one shape of data (name, price, qty), not a
  family of behaviours. NO inheritance for "coin" — a denomination is just an int.

STEP 3 — PATTERN? (what varies?)
  This is the textbook home for the STATE pattern (IDLE / HAS_SELECTION / DISPENSING as classes
  that change what insert_coin/select/dispense do). For an EASY problem with only two behavioural
  states and a handful of rules, a full State class hierarchy is over-engineering — we model the
  state as a single field (self._selected is None or not) and branch on it. Say the seam out loud:
  "if this grew states (OUT_OF_SERVICE, MAINTENANCE, COIN_JAM) I'd promote this to real State
  classes so each state file only knows its own legal transitions" — but don't build it unpromoted.

STEP 4 — SOLID (+ CONCURRENCY note)
  SRP  VendingMachine owns two concerns that are small enough to share a class here: inventory
       (add_product) and the transaction lifecycle (insert_coin/select/dispense/refund). If this
       grew, split into Inventory + a TransactionController that references it (aggregation).
  OCP  Adding a new product is pure data (add_product); no method changes to add a SKU.
  CONCURRENCY  Two buyers select the LAST unit of the same product concurrently: both read
       qty==1>0 as "available", both proceed to dispense, quantity goes negative. Fix: make the
       "check qty, then decrement" step ATOMIC — lock per product code (or one lock around the
       small select/dispense critical section), not one giant lock around the whole machine which
       would serialize buyers on unrelated products for no reason.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (object flow / a run-through) ─────────────────────
#   m = VendingMachine()                        # empty machine, no products yet
#   m.add_product("A1", "Water", price=15, quantity=2)   # stock 2 units of Water @ 15
#   m.state                                      # "IDLE"           (nothing selected)
#   m.select("A1")                               # code known + in stock -> selected = "A1"
#   m.state                                      # "HAS_SELECTION"
#   m.insert_coin(10); m.insert_coin(10)         # balance: 10 -> 20
#   name, change = m.dispense()                  # balance(20) >= price(15) -> qty A1: 2->1
#                                                 #   -> ("Water", 5)  and machine resets to IDLE
#   m.balance                                    # 0   (cleared after dispense)
#   m.state                                      # "IDLE"
#   # A caller who changes their mind instead calls m.refund() to get their coins back and
#   # clear the selection without buying anything.
#   # Flow: buyer -> insert_coin/select (mutate balance/selection) -> dispense (validate, pay out,
#   #        decrement inventory, reset to IDLE).
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# class VendingError(Exception):
#     pass


# class VendingMachine:
#     def __init__(self):
#         # LOGIC: code -> [name, price, quantity]. A short list is enough for 3 fields; a dataclass
#         # would also work but adds a class for no real behavioural gain here.
#         self.products = {}
#         self._balance = 0          # coins inserted since the last dispense/refund
#         self._selected = None      # None = IDLE; a product code string = HAS_SELECTION

#     def add_product(self, code, name, price, quantity):
#         # "Stock (or restock)": always (re)write the full slot, so calling it again with a new
#         # quantity simply replaces the old stock level for that code.
#         self.products[code] = [name, price, quantity]

#     def insert_coin(self, denomination):
#         # LOGIC: coins can be inserted whether idle or mid-selection — just accumulate.
#         self._balance += denomination

#     def select(self, code):
#         product = self.products.get(code)         # .get -> None if the code was never stocked
#         if product is None:
#             raise VendingError(f"unknown product code: {code}")
#         if product[2] <= 0:                        # product[2] = quantity
#             raise VendingError(f"out of stock: {code}")
#         self._selected = code                       # moves state IDLE -> HAS_SELECTION

#     def dispense(self):
#         if self._selected is None:
#             raise VendingError("no product selected")
#         name, price, qty = self.products[self._selected]
#         if self._balance < price:
#             # LOGIC: guard fails BEFORE any mutation, so balance/selection are left untouched —
#             # the test explicitly checks balance is preserved after a failed dispense.
#             raise VendingError("insufficient balance")
#         change = self._balance - price               # e.g. balance 20 - price 15 = 5
#         self.products[self._selected][2] -= 1         # decrement stock for the dispensed unit
#         self._balance = 0                              # reset to IDLE...
#         self._selected = None                          # ...both conditions of IDLE cleared together
#         return (name, change)

#     def refund(self):
#         # LOGIC: hand back whatever was inserted and cancel the in-progress selection, without
#         # touching inventory (nothing was dispensed).
#         amount = self._balance
#         self._balance = 0
#         self._selected = None
#         return amount

#     @property
#     def balance(self):
#         return self._balance

#     @property
#     def state(self):
#         # LOGIC: state is DERIVED from _selected rather than stored redundantly, so it can never
#         # drift out of sync with the real selection.
#         return "IDLE" if self._selected is None else "HAS_SELECTION"
