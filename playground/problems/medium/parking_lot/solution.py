"""
PARKING LOT — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

The solution below the marker is COMMENTED OUT. Read the reasoning, then write your own
active version (or strip the leading "# " from each line) and run:
    python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Vehicles of types park in compatible spots; issue a ticket; bill by duration on exit."
    nouns -> ParkingLot, Spot, Vehicle, Ticket ; types = SMALL/MED/LARGE, MOTORCYCLE/CAR/TRUCK
    verbs -> park, unpark, count-available
  Vehicle/Spot TYPES are closed value sets → strings/enums, not class hierarchies.

STEP 2 — ENTITIES & RELATIONSHIPS
  ParkingLot ◆──── Spot        COMPOSITION: the lot owns its spots (created via add_spot,
                               die with the lot).
  Ticket ───▶ Spot, Vehicle    ASSOCIATION: a ticket REFERENCES the spot it occupies and the
                               vehicle; it doesn't own them.
  ParkingLot o──── clock, rates  DEPENDENCY INJECTION: the clock and price table are PASSED IN
                               (aggregation), not hard-coded — that's what makes fees testable
                               (DIP). Big beginner win: never call time.time() directly deep
                               in logic; inject it.
  NO inheritance for vehicle types — they differ by DATA (a required spot size), not behaviour.

STEP 3 — PATTERNS (what varies?)
  Two things vary and are classic Strategy seams:
    • WHICH spot to assign (best-fit here; could be nearest-to-gate, floor-balancing) → allocation Strategy.
    • HOW to price (hourly here; could be flat, day-pass, free-15-min) → pricing Strategy.
  For the base we keep them as simple methods but NAME the seam out loud — swap-in on request.
  Spot creation is a light Factory (add_spot builds the right spot). The single lot manager is
  a natural Singleton, but say "I'd inject it rather than a global — DI is more testable."
  Don't add all this machinery unless asked; mention it, keep the base simple (KISS).

STEP 4 — SOLID + CONCURRENCY (the SDE-2 bit)
  SRP  Spot = state of one bay; Ticket = a parking session; ParkingLot = allocation + billing.
  OCP  A new spot type / new pricing = new data/Strategy, not edits to park()/unpark().
  CONCURRENCY  Two cars race for the last compatible spot: both read "free", both take it →
       double-assign. Fix: claim a spot ATOMICALLY (lock per SPOT, or a lock around the small
       find-and-mark step) — NOT one global lock on the whole lot, which serialises every gate
       and kills throughput. This is THE follow-up; have the fine-grained-locking answer ready.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (a car parks, then leaves) ────────────────────────
#   clock = FakeClock(0)                       # inject a controllable clock (real code: omit → time.time)
#   lot = ParkingLot(clock=clock)              # empty lot; clock + rate table injected (DI)
#   lot.add_spot("S1","SMALL"); lot.add_spot("M1","MEDIUM"); lot.add_spot("L1","LARGE")
#   t = lot.park("CAR-9", "CAR")               # best-fit: smallest free spot that fits a car → M1 → mark taken
#                                              #   → record entry = clock() → return ticket "TK1"
#   lot.available_count("MEDIUM")              # 0  (the car took M1)
#   clock.t = 3600 * 2                          # 2 hours pass (tests bump the injected clock)
#   fee = lot.unpark(t)                        # look up ticket → free the spot → ceil(hours)*rate → 40
#   # Flow:  entry gate → ParkingLot.park (reads spots, writes a ticket) ;  exit → unpark (frees spot, bills).
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import time
# import math
# import itertools


# class ParkingFull(Exception):
#     pass


# class InvalidTicket(Exception):
#     pass


# # LOGIC: give sizes a NUMERIC order so "does a spot fit?" becomes a number comparison. SMALL<MED<LARGE.
# SIZE = {"SMALL": 0, "MEDIUM": 1, "LARGE": 2}
# # LOGIC: the SMALLEST size each vehicle can use. A motorcycle fits any spot (needs size ≥ 0), a car
# # needs MEDIUM or bigger (≥ 1), a truck only LARGE (≥ 2). So "fits" == spot_size >= REQUIRED[vehicle].
# REQUIRED = {"MOTORCYCLE": 0, "CAR": 1, "TRUCK": 2}
# DEFAULT_RATES = {"MOTORCYCLE": 10, "CAR": 20, "TRUCK": 30}   # per-hour price by vehicle type


# class ParkingLot:
#     def __init__(self, clock=None, hourly_rates=None):
#         # DI: `clock or time.time` means "use the injected clock, else fall back to the real one".
#         # Tests pass a fake clock so fees are deterministic; production passes nothing → time.time.
#         self.clock = clock or time.time
#         self.rates = hourly_rates or DEFAULT_RATES
#         self.spots = {}      # spot_id -> [type, occupied?]   (a spot is tiny state → a 2-item list)
#         self.tickets = {}    # ticket_id -> [spot_id, vehicle_type, entry_time, open?]
#         self._seq = itertools.count(1)   # 1,2,3... → unique ticket numbers

#     def add_spot(self, spot_id, spot_type):
#         self.spots[spot_id] = [spot_type, False]     # False = not occupied yet

#     def available_count(self, spot_type=None):
#         # LOGIC: count spots that are free (not occ) AND (no type filter, or matching that type).
#         # `sum(1 for ... if cond)` is the idiomatic "count items matching a condition".
#         return sum(1 for t, occ in self.spots.values()
#                    if not occ and (spot_type is None or t == spot_type))

#     def park(self, vehicle_id, vehicle_type):
#         need = REQUIRED[vehicle_type]                # minimum size this vehicle needs
#         # BEST-FIT ALLOCATION: build (size, spot_id) for every FREE spot big enough (SIZE[t] >= need).
#         # sorted() orders by the first tuple element (size) ascending, so candidates[0] is the
#         # SMALLEST spot that still fits → we don't waste a LARGE bay on a motorcycle.
#         candidates = sorted(
#             (SIZE[t], sid) for sid, (t, occ) in self.spots.items()
#             if not occ and SIZE[t] >= need
#         )
#         if not candidates:                           # empty list → nothing fits/free
#             raise ParkingFull("no compatible spot free")
#         spot_id = candidates[0][1]                   # [0] = smallest, [1] = its spot_id
#         # --- find-then-mark: THIS is the critical section a concurrency follow-up must lock ---
#         self.spots[spot_id][1] = True                # mark occupied
#         ticket_id = f"TK{next(self._seq)}"
#         # snapshot entry time NOW via the injected clock; we'll diff against exit time to bill.
#         self.tickets[ticket_id] = [spot_id, vehicle_type, self.clock(), True]
#         return ticket_id

#     def unpark(self, ticket_id):
#         t = self.tickets.get(ticket_id)              # .get → None if unknown (no KeyError)
#         if not t or not t[3]:                        # unknown ticket, OR t[3] is False = already closed
#             raise InvalidTicket("bad or reused ticket")
#         spot_id, vtype, entry, _ = t                 # unpack the ticket
#         self.spots[spot_id][1] = False               # free the bay for the next car
#         t[3] = False                                 # close the ticket so it can't be unparked twice
#         # PRICING: duration in seconds → hours, ROUND UP (a part-hour bills as a full hour), min 1h.
#         # math.ceil(90s/3600) = ceil(0.025) = 1;  ceil((2h+1s)/3600) = ceil(2.0002) = 3.
#         hours = max(1, math.ceil((self.clock() - entry) / 3600))
#         return hours * self.rates[vtype]
