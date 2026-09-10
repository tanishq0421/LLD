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


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6 · SDE-1 → SDE-2 UPGRADES — the follow-ups written AS CODE
#          Same problem. The level difference is in the depth of these answers, not the base.
# ═══════════════════════════════════════════════════════════════════════════════
#
# ───────────────────────────────────────────────────────────────────────────────
# (A) CONCURRENCY / THREAD-SAFETY   ← the #1 follow-up, the biggest SDE-1→SDE-2 jump
# ───────────────────────────────────────────────────────────────────────────────
# THE BUG (why the base park() is unsafe): two cars call park() at the same instant. Both run the
# "find a free spot" READ, both see spot L1 free, both then MARK it taken → one spot, two cars.
# It's a textbook check-then-act race on shared state (self.spots).
#   Measured (200 cars racing for 50 spots):  no lock → ~190 "succeed" (huge oversell);
#                                             locked  → exactly 50.  The lock IS the difference.
#
# THE FIX — make find-and-mark ONE atomic step. The whole diff vs the base class:
#
#   import threading
#   class ParkingLot:
#       def __init__(self, clock=None, hourly_rates=None):
#           ...
#           self._lock = threading.Lock()                 # <── ADDED
#
#       def park(self, vehicle_id, vehicle_type):
#           need = REQUIRED[vehicle_type]
#           with self._lock:                              # <── ADDED: wrap ONLY the critical section
#               candidates = sorted(                      #     (the READ …)
#                   (SIZE[t], sid) for sid, (t, occ) in self.spots.items()
#                   if not occ and SIZE[t] >= need)
#               if not candidates:
#                   raise ParkingFull("no compatible spot free")
#               spot_id = candidates[0][1]
#               self.spots[spot_id][1] = True             #     … and the WRITE — now inseparable)
#               ticket_id = f"TK{next(self._seq)}"
#               self.tickets[ticket_id] = [spot_id, vehicle_type, self.clock(), True]
#               return ticket_id
#
#       def unpark(self, ticket_id):                      # unpark() also mutates self.spots →
#           with self._lock:                              # guard it too, else a free() can race a park()
#               ...  # (same body as the base unpark)
#
# WHAT TO SAY OUT LOUD (this narration is the real SDE-2 signal, more than the code):
#   • "Only find-a-spot + mark-it must be atomic, so I lock exactly those lines — not the whole
#      method. Building the ticket id / timestamp doesn't touch shared state, it can stay outside."
#   • GLOBAL vs FINE-GRAINED (the senior nuance the interviewer is fishing for):
#       – ONE lock on the whole lot (above) is CORRECT but serialises EVERY gate → throughput is
#         capped at one core; two cars at opposite ends of the lot still wait on each other.
#       – FINER: a lock PER SPOT (or per floor / per spot-type bucket) → unrelated cars never block.
#       – OPTIMISTIC: compare-and-set on each spot's occupied flag, retry on conflict → no blocking
#         on the happy path (great when contention is rare).
#       – AT DB SCALE: `SELECT … FOR UPDATE` on the spot row, or a UNIQUE constraint on the
#         assignment so the DB itself rejects the second claim.
#   • The trade-off to name: coarse lock = simple + correct + low throughput; fine-grained = more
#     complex + scales. Pick coarse first, then say how you'd shard it. (Don't build all of it.)
#
# ───────────────────────────────────────────────────────────────────────────────
# (B) PRICING as a STRATEGY   ← "now support a flat fee / day-pass / free-first-15-min"
# ───────────────────────────────────────────────────────────────────────────────
# SDE-1: the fee formula lives INSIDE unpark(). Every new tariff = edit unpark() (you can break
#        existing pricing while adding a new one).
# SDE-2: make pricing a swappable Strategy, injected in → a new tariff is a NEW class, unpark()
#        never changes (Open/Closed Principle).
#
#   class HourlyPricing:
#       def fee(self, vehicle_type, seconds):
#           return max(1, math.ceil(seconds / 3600)) * DEFAULT_RATES[vehicle_type]
#
#   class FlatPricing:
#       def __init__(self, amount): self.amount = amount
#       def fee(self, vehicle_type, seconds): return self.amount
#
#   class FreeFirst15Pricing:                      # free for ≤15 min, hourly after
#       def fee(self, vehicle_type, seconds):
#           if seconds <= 15 * 60: return 0
#           return max(1, math.ceil(seconds / 3600)) * DEFAULT_RATES[vehicle_type]
#
#   # inject it, then DELEGATE instead of computing inline:
#   def __init__(self, ..., pricing=None):
#       self.pricing = pricing or HourlyPricing()          # DI; default keeps base behaviour
#   def unpark(self, ticket_id):
#       ...
#       return self.pricing.fee(vtype, self.clock() - entry)   # unpark() no longer KNOWS the formula
#
# Same move for ALLOCATION: BestFit (base) vs NearestToGate vs FloorBalancing → an AllocationStrategy
# with pick(spots, need) -> spot_id, injected the same way. Base picks a default; interviewer swaps it.
#
# ───────────────────────────────────────────────────────────────────────────────
# (C) OTHER FOLLOW-UPS (sketch — MENTION, don't over-build; over-building is a red flag):
# ───────────────────────────────────────────────────────────────────────────────
#   • MULTI-FLOOR:   give Spot a `floor`; the lot holds floors; allocation scans floors in policy
#                    order. park()'s SHAPE doesn't change — only the candidate set it searches.
#   • DISPLAY BOARD ("3 left"): Observer — the lot notifies subscribed displays on park/unpark.
#   • EV / HANDICAPPED spots: new spot TYPES (data), not new classes — exactly why `type` is a
#     string/enum, not a subclass. New type = one dict entry, zero edits to park().
#
# ───────────────────────────────────────────────────────────────────────────────
# SDE-1  vs  SDE-2  AT A GLANCE  (same problem — what raises the bar):
#   Correctness     happy-path park/unpark works       + the last-spot RACE handled with a lock
#   Extensibility   one pricing rule, edit to change   pricing & allocation are injected Strategies (OCP)
#   Concurrency     "I'd put a lock"                   global-vs-fine-grained + the throughput trade-off
#   Communication   explains what the code does        narrates trade-offs & when NOT to add machinery
# ═══════════════════════════════════════════════════════════════════════════════
