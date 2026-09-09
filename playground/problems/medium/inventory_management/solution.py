"""
INVENTORY MANAGEMENT — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

WHY THIS ONE FOR BLINKIT: dark-store stock with checkout holds is exactly this, and the
"two orders grab the last unit" race is the concurrency follow-up they love. Have that answer
crisp.

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES
  "SKUs with stock; reserve at checkout; confirm on payment; release on abandon."
    nouns -> Product(stock), Reservation, Inventory ; verbs -> add, reserve, confirm, release

STEP 2 — ENTITIES & RELATIONSHIPS
  Inventory ◆──── Product      COMPOSITION: the inventory owns the per-SKU stock records.
  Inventory ◆──── Reservation  COMPOSITION: reservations live inside the inventory.
  Reservation ───▶ Product     ASSOCIATION: a reservation points at the SKU it holds.

STEP 3 — THE KEY MODEL (this is the whole insight)
  Track TWO numbers per SKU:  on_hand (physical) and reserved (held for in-flight checkouts).
      available = on_hand − reserved
  • reserve(qty): DON'T touch on_hand — just increase `reserved` (the unit is spoken-for but
    still physically present). Fails if available < qty.
  • confirm():   payment succeeded → the unit really leaves: on_hand −= qty, reserved −= qty.
  • release():   checkout abandoned → give it back: reserved −= qty (on_hand unchanged).
  This two-phase (reserve → confirm/release) is what prevents overselling AND lets you free
  stock when a customer bails. NO GoF pattern needed — the model is the point.

STEP 4 — CONCURRENCY (THE follow-up — rehearse this)
  Race: two checkouts both call reserve(sku, 1) for the last unit. Both read available=1, both
  think "ok", both increment reserved → oversell. FIX: make the check-and-increment ATOMIC.
      • lock PER SKU (fine-grained) so different SKUs don't block each other — preferred, and
        say WHY: one global lock serialises all reservations and kills throughput.
      • or an atomic compare-and-set on the counter.
  At scale the atomic decrement moves to the DB/Redis (a Lua script / conditional update).
  SRP note: reserve/confirm/release each do one transition; available() is a pure read.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (checkout hold → pay or abandon) ──────────────────
#   inv = Inventory(); inv.add_product("milk", 5)   # on_hand=5, reserved=0 → available 5
#   r = inv.reserve("milk", 2)                       # available≥2 → reserved=2 → available 3 (on_hand still 5)
#   inv.confirm(r)                                   # PAID → on_hand 3, reserved 0 → available 3 (unit truly left)
#   r2 = inv.reserve("milk", 1)                      # hold 1 → available 2
#   inv.release(r2)                                  # ABANDONED → reserved back → available 3 again
#   inv.reserve("milk", 99)                          # available < 99 → InventoryError (never oversell)
#   # Flow:  add-to-cart/checkout → reserve (lock: check+increment) ; payment → confirm ; timeout → release.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import threading
# import itertools


# class InventoryError(Exception):
#     pass


# class Inventory:
#     def __init__(self):
#         self.products = {}      # sku -> {"on_hand": int, "reserved": int}
#         self.reservations = {}  # reservation_id -> {"sku", "qty", "active"}
#         # ONE lock guards the check-and-modify below. (Interview upgrade: a lock PER SKU so
#         # different products don't serialise — mention it even if you code the simple one.)
#         self._lock = threading.Lock()
#         self._seq = itertools.count(1)

#     def add_product(self, sku, quantity):
#         self.products[sku] = {"on_hand": quantity, "reserved": 0}

#     def restock(self, sku, qty):
#         if sku not in self.products:
#             raise InventoryError("unknown sku")
#         self.products[sku]["on_hand"] += qty

#     def available(self, sku):
#         if sku not in self.products:
#             raise InventoryError("unknown sku")
#         p = self.products[sku]
#         return p["on_hand"] - p["reserved"]     # the core formula

#     def reserve(self, sku, qty):
#         # CRITICAL SECTION: the check (available >= qty) and the update (reserved += qty) must be
#         # ONE atomic step, or two threads oversell the last unit.
#         with self._lock:
#             if sku not in self.products:
#                 raise InventoryError("unknown sku")
#             p = self.products[sku]
#             if p["on_hand"] - p["reserved"] < qty:
#                 raise InventoryError("insufficient stock")
#             p["reserved"] += qty
#             rid = f"R{next(self._seq)}"
#             self.reservations[rid] = {"sku": sku, "qty": qty, "active": True}
#             return rid

#     def confirm(self, reservation_id):
#         with self._lock:
#             r = self.reservations.get(reservation_id)
#             if not r or not r["active"]:            # unknown or already used → invalid
#                 raise InventoryError("bad reservation")
#             p = self.products[r["sku"]]
#             p["on_hand"] -= r["qty"]                # the unit physically leaves now
#             p["reserved"] -= r["qty"]               # ...and is no longer merely held
#             r["active"] = False

#     def release(self, reservation_id):
#         with self._lock:
#             r = self.reservations.get(reservation_id)
#             if not r or not r["active"]:
#                 raise InventoryError("bad reservation")
#             self.products[r["sku"]]["reserved"] -= r["qty"]   # give the hold back
#             r["active"] = False
