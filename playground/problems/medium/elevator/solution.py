"""
ELEVATOR (single car, LOOK) — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "An elevator receives floor requests and services them efficiently (LOOK), not FCFS. Model
   moving up/down/idle and one-floor-per-step motion."
    nouns -> Elevator (current_floor, direction, targets) ; verbs -> request_floor, step

STEP 2 — ENTITIES & RELATIONSHIPS
  Elevator ◆──── targets (a set of floors)   COMPOSITION: the pending-request set lives and dies
                                              with the elevator; nothing else references it.
  Elevator ───▶ direction (IDLE/UP/DOWN)     the direction is elevator STATE, not a separate
                                              object for the base version (see STEP 3 on why we
                                              don't build a full State-pattern class hierarchy here).
  NO separate Request/FloorButton class — a target is just an int in a set; it carries no data of
  its own (no "who pressed it" / "when"), so a class would be pure ceremony over one integer.

STEP 3 — PATTERN? (what varies?)
  Conceptually this IS the State pattern (IDLE / MOVING_UP / MOVING_DOWN each interpret `step()`
  differently) — but implementing it as three literal classes for THREE STRING VALUES is
  over-engineering for the base problem: each "state" here differs by one branch, not by a
  meaningfully different set of behaviours or fields. We keep `direction` as a plain string and
  branch on it — and SAY OUT LOUD in an interview that DOORS_OPEN/MAINTENANCE/EMERGENCY (the
  follow-ups) are exactly where a real State class hierarchy earns its keep, because those states
  have genuinely different rules (e.g. EMERGENCY ignores new requests entirely; a string can't
  express "and also reject this method call").
  Dispatch across MULTIPLE elevators (which car answers a hall call) is the named Strategy seam —
  out of scope for a single car, but the natural next question.

STEP 4 — SOLID (+ CONCURRENCY)
  SRP   Elevator owns motion + scheduling only; a controller (not built here) would own multiple
        cars + dispatch.
  OCP   a new scheduling policy (e.g. prioritize VIP floors) swaps the "pick next target" step
        without touching request_floor's validation or the one-floor-per-step motion.
  CONCURRENCY  a request can arrive from a hall button WHILE step() is running (different thread).
        `targets` is mutated by both `request_floor` (add) and `step` (remove/read) — guard both
        with one lock scoped to this car (a `set` isn't atomic across add+iterate). Multiple cars
        share no state, so this lock never needs to span more than one Elevator.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (LOOK: serve the near side, then reverse) ─────────
#   e = Elevator(current_floor=3, max_floor=10)
#   e.request_floor(6); e.request_floor(1)          # targets = {1, 6}; direction still IDLE
#   e.step()                                          # IDLE -> nearest target is 1 (below) -> DOWN, moves to 2
#   e.direction                                       # "DOWN"
#   e.step(); e.step()                                # 2->1 (services 1, removed from targets)
#   e.targets                                         # {6}      (1 has been serviced)
#   # ...continuing to step(): LOOK finds nothing left going DOWN -> reverses to UP -> climbs to 6
#   # Flow: step() -> on-target? service in place : has-targets? keep-or-reverse then move one
#   #       floor : else -> IDLE. Direction never changes mid-move, only when nothing's left ahead.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# class Elevator:
#     def __init__(self, current_floor=0, min_floor=0, max_floor=10):
#         self.current_floor = current_floor
#         self.min_floor = min_floor
#         self.max_floor = max_floor
#         self._direction = "IDLE"
#         self._targets = set()

#     @property
#     def direction(self):
#         return self._direction

#     @property
#     def targets(self):
#         return set(self._targets)          # copy — callers can't mutate our internal state

#     def request_floor(self, floor):
#         if not (self.min_floor <= floor <= self.max_floor):
#             raise ValueError(f"floor {floor} outside [{self.min_floor}, {self.max_floor}]")
#         self._targets.add(floor)           # requesting the current floor is fine — see below

#     def step(self):
#         # LOGIC: if we're STANDING on a requested floor, servicing it IS this step's action — the
#         # car doesn't also move. (This is why request_floor(current_floor) is valid: it gets
#         # serviced on the very next step() instead of being silently ignored.)
#         if self.current_floor in self._targets:
#             self._targets.discard(self.current_floor)
#             return

#         if not self._targets:
#             # LOGIC: nothing left to do -> go IDLE. (No-op if already idle.)
#             self._direction = "IDLE"
#             return

#         if self._direction == "IDLE":
#             # LOGIC: from a standstill, LOOK picks up whichever direction the NEAREST target is
#             # in. Example: at floor 3 with targets {1, 6} -> |1-3|=2 is nearer than |6-3|=3 -> DOWN.
#             nearest = min(self._targets, key=lambda f: abs(f - self.current_floor))
#             self._direction = "UP" if nearest > self.current_floor else "DOWN"
#         elif self._direction == "UP":
#             # LOGIC: keep climbing only while some target is still AHEAD (above us); once every
#             # remaining target is behind, reverse. This is the "L" turn of LOOK — no wasted trip
#             # to the very top floor if nothing up there is requested.
#             if not any(f > self.current_floor for f in self._targets):
#                 self._direction = "DOWN"
#         elif self._direction == "DOWN":
#             if not any(f < self.current_floor for f in self._targets):
#                 self._direction = "UP"

#         # LOGIC: move exactly one floor in whatever direction we just settled on.
#         self.current_floor += 1 if self._direction == "UP" else -1
