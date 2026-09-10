"""
RIDE-HAILING SERVICE — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Drivers sit at locations; a rider requests a ride; the nearest free driver is assigned;
   a trip moves ASSIGNED -> ONGOING -> COMPLETED (or CANCELLED from either); ending prices
   the trip and frees the driver at the drop point."
    nouns -> RideService, Driver, Trip ; verbs -> register_driver, request_ride, start_trip,
    end_trip, cancel_trip
  Driver/Trip are tiny bags of mutable state (location, busy?, status) — plain dicts of
  fields are enough; no behavior of their own beyond "hold current state" (YAGNI on classes).

STEP 2 — ENTITIES & RELATIONSHIPS
  RideService ◆──── Driver     COMPOSITION: the service owns the driver registry.
  RideService ◆──── Trip       COMPOSITION: the service owns every trip it creates.
  Trip ───▶ Driver             ASSOCIATION: a trip REFERENCES the driver_id assigned to it;
                                it doesn't own the driver (the driver outlives any one trip).
  RideService o──── pricing    DEPENDENCY INJECTION: the fare function is PASSED IN (like the
                                clock in parking_lot) — default is 50 + 10*distance, but tests
                                inject a custom lambda. Never hardcode pricing math in end_trip.
  NO inheritance for trip status — "ASSIGNED/ONGOING/COMPLETED/CANCELLED" is a closed set of
  labels driving a transition table, not a type hierarchy.

STEP 3 — PATTERN? (what varies?)
  Two seams, both classic Strategy:
    • MATCHING — which free driver gets the ride. Here: nearest by Manhattan distance,
      tie-break by driver_id. Could swap for "highest rated" or "surge zone" — same call site.
    • PRICING — how distance becomes a fare. Injected as a callable so it's swappable/testable
      without touching request_ride/end_trip at all (OCP in action, not just a slogan).
  Trip status is a small STATE machine (ASSIGNED->ONGOING->COMPLETED, or ->CANCELLED from
  ASSIGNED/ONGOING) enforced by a transition table, not a big if/elif ladder scattered
  across methods.

STEP 4 — SOLID + CONCURRENCY (the SDE-2 bit)
  SRP  Driver dict = where/whether a driver is free; Trip dict = one ride's lifecycle;
       RideService = matching + transitions + pricing orchestration.
  OCP  A new matching rule or pricing rule = a new function/Strategy, not edits to the state
       machine. A new trip status = one more entry in the transition table.
  CONCURRENCY (the follow-up, exactly like BookMyShow's seat race): two riders call
  request_ride() at once when only ONE driver is free. Both must NOT see him as "free" and
  both get assigned — that's a double-assign, identical in shape to a double-sold seat.
    • Fix: the "find nearest free driver" SCAN and the "mark him busy" WRITE must be ONE
      atomic critical section — protected by a single lock (find-then-mark is a small,
      fast region, so one lock here is fine; unlike BookMyShow there's no natural per-entity
      lock key before you've even picked the entity, since the whole POINT of the critical
      section is deciding WHICH driver to lock).
    • Better throughput at scale: partition drivers into geo-buckets, lock the bucket you're
      matching within rather than the whole fleet.
    • DB analogy: `UPDATE drivers SET busy=true WHERE id=? AND busy=false` and checking the
      affected-row count, or `SELECT ... FOR UPDATE` on the candidate row.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (match, drive, complete) ───────────────────────────
#   svc = RideService()                          # default pricing: 50 + 10*distance
#   svc.register_driver("d1", 0, 0)
#   svc.register_driver("d2", 10, 10)
#   trip = svc.request_ride("r1", 1, 1)          # nearest free: d1 (dist 2) beats d2 (dist 18)
#                                                 #   -> mark d1 busy, trip "ASSIGNED", return "T1"
#   svc.get_driver(trip)                         # "d1"
#   svc.start_trip(trip)                         # "ASSIGNED" -> "ONGOING"
#   fare = svc.end_trip(trip, 3, 4)              # Manhattan(0,0 -> 3,4)=7 -> 50+70=120
#                                                 #   -> trip "COMPLETED"; d1 freed AT (3,4)
#   svc.trip_status(trip)                        # "COMPLETED"
#   svc.request_ride("r2", 3, 4)                 # d1 is free again, now sitting at (3,4)
#   # Flow: request_ride scans free drivers under a lock (atomic find-and-mark) -> start_trip/
#   # end_trip/cancel_trip walk a small transition table -> end_trip prices via the injected
#   # pricing(distance) callable and relocates+frees the driver at the drop point.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import itertools
# import threading


# class NoDriverAvailable(Exception):
#     pass


# class InvalidTrip(Exception):
#     pass


# def _distance(a, b):
#     # LOGIC: Manhattan distance — grid-city distance, no diagonals. dist((0,0),(3,4)) = 3+4 = 7.
#     return abs(a[0] - b[0]) + abs(a[1] - b[1])


# def _default_pricing(distance):
#     return 50 + 10 * distance


# # LOGIC: transition table — from_status -> to_status for each verb. Anything not listed here
# # (e.g. calling start_trip on an already-ONGOING trip) is illegal -> InvalidTrip. This keeps
# # the legality rule as DATA instead of a scattered if/elif chain per method.
# _START_TRANSITIONS = {"ASSIGNED": "ONGOING"}
# _END_TRANSITIONS = {"ONGOING": "COMPLETED"}
# _CANCEL_FROM = {"ASSIGNED", "ONGOING"}


# class RideService:
#     def __init__(self, pricing=None):
#         self.pricing = pricing or _default_pricing   # DI: swap fare math without touching logic
#         self.drivers = {}   # driver_id -> {"x","y","busy"}
#         self.trips = {}     # trip_id -> {"rider_id","driver_id","pickup":(x,y),"status"}
#         self._seq = itertools.count(1)
#         # LOGIC: ONE lock guarding "scan free drivers, then mark the chosen one busy" — the
#         # critical section from STEP 4. It must wrap BOTH the read (who's free) and the write
#         # (claim the driver), or two threads can both read "free" before either writes "busy".
#         self._match_lock = threading.Lock()

#     def register_driver(self, driver_id, x, y):
#         # LOGIC: (re)registering always resets busy=False — a driver coming back online is free.
#         self.drivers[driver_id] = {"x": x, "y": y, "busy": False}

#     def request_ride(self, rider_id, x, y):
#         pickup = (x, y)
#         with self._match_lock:   # atomic find-then-mark: see STEP 4 concurrency note
#             # LOGIC: candidates = (distance, driver_id) for every FREE driver. sorted() orders
#             # by distance first, driver_id second (tuple comparison) -> candidates[0] is the
#             # nearest driver, ties broken by the smaller driver_id — deterministic, testable.
#             candidates = sorted(
#                 (_distance(pickup, (d["x"], d["y"])), driver_id)
#                 for driver_id, d in self.drivers.items() if not d["busy"]
#             )
#             if not candidates:
#                 raise NoDriverAvailable("no free driver")
#             driver_id = candidates[0][1]
#             self.drivers[driver_id]["busy"] = True    # claim BEFORE releasing the lock
#             trip_id = f"T{next(self._seq)}"
#             self.trips[trip_id] = {
#                 "rider_id": rider_id,
#                 "driver_id": driver_id,
#                 "pickup": pickup,
#                 "status": "ASSIGNED",
#             }
#             return trip_id

#     def start_trip(self, trip_id):
#         trip = self.trips[trip_id]                 # KeyError propagates for unknown trip_id
#         # LOGIC: .get(status) -> None if status has no entry in the table -> falls into the
#         # `else raise` branch just like an explicitly-illegal transition would.
#         next_status = _START_TRANSITIONS.get(trip["status"])
#         if next_status is None:
#             raise InvalidTrip(f"cannot start trip in status {trip['status']}")
#         trip["status"] = next_status

#     def end_trip(self, trip_id, drop_x, drop_y):
#         trip = self.trips[trip_id]
#         next_status = _END_TRANSITIONS.get(trip["status"])
#         if next_status is None:
#             raise InvalidTrip(f"cannot end trip in status {trip['status']}")
#         distance = _distance(trip["pickup"], (drop_x, drop_y))
#         fare = self.pricing(distance)
#         trip["status"] = next_status
#         # LOGIC: free the driver AT the drop point — their next match starts from here, not
#         # from where they picked the rider up (that's the point of test_driver_freed_after_trip).
#         driver = self.drivers[trip["driver_id"]]
#         driver["x"], driver["y"] = drop_x, drop_y
#         driver["busy"] = False
#         return fare

#     def cancel_trip(self, trip_id):
#         trip = self.trips[trip_id]
#         if trip["status"] not in _CANCEL_FROM:
#             raise InvalidTrip(f"cannot cancel trip in status {trip['status']}")
#         trip["status"] = "CANCELLED"
#         # LOGIC: the trip never reached a drop point, so the driver is freed at their CURRENT
#         # (unchanged) location — no need to touch x/y, just flip busy back off.
#         self.drivers[trip["driver_id"]]["busy"] = False

#     def trip_status(self, trip_id):
#         return self.trips[trip_id]["status"]        # KeyError if unknown

#     def get_driver(self, trip_id):
#         return self.trips[trip_id]["driver_id"]      # KeyError if unknown
