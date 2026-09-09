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


# # Size ORDER lets us compare "does this spot fit?" numerically and pick the SMALLEST that fits.
# SIZE = {"SMALL": 0, "MEDIUM": 1, "LARGE": 2}
# # The minimum spot size each vehicle needs (motorcycle fits anything, truck needs LARGE).
# REQUIRED = {"MOTORCYCLE": 0, "CAR": 1, "TRUCK": 2}
# DEFAULT_RATES = {"MOTORCYCLE": 10, "CAR": 20, "TRUCK": 30}


# class ParkingLot:
#     def __init__(self, clock=None, hourly_rates=None):
#         # DI: default to the real clock/rates, but let tests inject fakes. This one line is
#         # why fees are deterministically testable.
#         self.clock = clock or time.time
#         self.rates = hourly_rates or DEFAULT_RATES
#         self.spots = {}      # spot_id -> [type, occupied?]  (a spot is small state → a list is fine)
#         self.tickets = {}    # ticket_id -> [spot_id, vehicle_type, entry_time, open?]
#         self._seq = itertools.count(1)   # source of unique ticket ids

#     def add_spot(self, spot_id, spot_type):
#         self.spots[spot_id] = [spot_type, False]

#     def available_count(self, spot_type=None):
#         return sum(1 for t, occ in self.spots.values()
#                    if not occ and (spot_type is None or t == spot_type))

#     def park(self, vehicle_id, vehicle_type):
#         need = REQUIRED[vehicle_type]
#         # ALLOCATION STRATEGY (best-fit): among free spots big enough, pick the SMALLEST, so a
#         # motorcycle doesn't waste a LARGE bay. Sorting by size gives best-fit for free.
#         candidates = sorted(
#             (SIZE[t], sid) for sid, (t, occ) in self.spots.items()
#             if not occ and SIZE[t] >= need
#         )
#         if not candidates:
#             raise ParkingFull("no compatible spot free")
#         spot_id = candidates[0][1]
#         # --- this find-then-mark is the critical section a concurrency follow-up must lock ---
#         self.spots[spot_id][1] = True
#         ticket_id = f"TK{next(self._seq)}"
#         self.tickets[ticket_id] = [spot_id, vehicle_type, self.clock(), True]
#         return ticket_id

#     def unpark(self, ticket_id):
#         t = self.tickets.get(ticket_id)
#         if not t or not t[3]:                     # unknown, or already closed → invalid
#             raise InvalidTicket("bad or reused ticket")
#         spot_id, vtype, entry, _ = t
#         self.spots[spot_id][1] = False            # free the bay
#         t[3] = False                              # close the ticket (so it can't be reused)
#         # PRICING STRATEGY (hourly, min 1h, round up): duration in hours * per-hour rate.
#         hours = max(1, math.ceil((self.clock() - entry) / 3600))
#         return hours * self.rates[vtype]
