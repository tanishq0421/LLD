"""
MEETING SCHEDULER — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

WHY THIS ONE FOR myKaarma: their product schedules service appointments into bays/time-slots —
this IS that problem. Nail the interval overlap rule and you've nailed their domain.

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES
  "Rooms; book [start,end); no overlap per room; find free rooms; cancel."
    nouns -> Room, Booking, Scheduler ; verbs -> book, is-available, find, cancel

STEP 2 — ENTITIES & RELATIONSHIPS
  Scheduler o──── Room        the scheduler manages rooms added to it.
  Room ◆──── Booking          COMPOSITION: a booking is a slot INSIDE a room's timeline; it has
                              no meaning without its room.
  Booking ───▶ Room           the booking id also maps back to its room (for cancel).

STEP 3 — PATTERN? (what varies?)
  Not much → NO GoF pattern needed for the base (resist over-engineering). The real content is
  the correct OVERLAP RULE, not machinery. `book_any` is a light allocation strategy (first-fit)
  you could later swap (least-used room, room-with-projector) — name that seam.

  ★ THE ONE RULE TO MEMORISE — half-open intervals [start, end):
      two intervals overlap  ⟺  start1 < end2  AND  start2 < end1
    Half-open means a meeting ending at 11:00 and one starting at 11:00 DON'T clash
    (11:00 is free). Getting this boundary right is the whole problem; most people fumble it.

STEP 4 — SOLID + SCALE + CONCURRENCY
  SRP  the overlap test is one tiny function; Room holds its own bookings; Scheduler coordinates.
  OCP  a new allocation rule = a new strategy, not edits to book().
  SCALE  linear scan is fine to state; "at scale I'd use an interval tree for O(log n) lookup."
  CONCURRENCY  two bookings for the last free room at the same instant → lock the check-and-insert.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (book a room, avoid a clash) ──────────────────────
#   s = MeetingScheduler()
#   s.add_room("R1"); s.add_room("R2")
#   b1 = s.book("R1", 10, 11)                  # is_available? yes → append to R1's timeline → "B1"
#   s.book("R1", 10, 12)                       # overlaps [10,11) → raises Conflict
#   s.book("R1", 11, 12)                       # 11 == previous end → half-open, no overlap → allowed
#   s.available_rooms(10, 11)                  # ["R2"]   (R1 is busy in that window)
#   room, b = s.book_any(10, 11)               # first-fit over rooms → ("R2", "B..")
#   s.cancel(b1)                               # frees [10,11) on R1 again
#   # Flow:  caller → Scheduler.book → overlaps() scan over THAT room's list → insert (or raise Conflict).
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import itertools


# class Conflict(Exception):
#     pass


# class NoRoomAvailable(Exception):
#     pass


# # THE HEART OF THE PROBLEM. Picture two bars on a number line:  A = [s1, e1),  B = [s2, e2).
# #   They MISS each other in only two ways:  A entirely before B  (e1 <= s2)
# #                                     or:    A entirely after  B  (e2 <= s1)
# #   They OVERLAP in every other case. Negate "miss": overlap == NOT(e1<=s2 or e2<=s1)
# #                                                            == (e1 > s2) and (e2 > s1)
# #                                                            == (s1 < e2) and (s2 < e1)   ← this line.
# #   Example: [10,11) vs [11,12) → s1<e2 (10<12 ✓) and s2<e1 (11<11 ✗) → False → NO clash (good,
# #   half-open lets back-to-back meetings share the boundary 11).
# def overlaps(s1, e1, s2, e2):
#     return s1 < e2 and s2 < e1


# class MeetingScheduler:
#     def __init__(self):
#         self.rooms = {}       # room_id -> list of (start, end, booking_id)   (that room's timeline)
#         self.bookings = {}    # booking_id -> (room_id, start, end)           (reverse index for cancel)
#         self._seq = itertools.count(1)

#     def add_room(self, room_id):
#         self.rooms[room_id] = []                          # a new room starts with an empty timeline

#     def is_available(self, room_id, start, end):
#         # LOGIC: available == the requested window overlaps NONE of this room's existing bookings.
#         # `any(...)` is True if even one overlaps; we want the opposite, hence `not any(...)`.
#         return not any(overlaps(start, end, s, e) for (s, e, _) in self.rooms[room_id])

#     def book(self, room_id, start, end):
#         if room_id not in self.rooms:
#             raise KeyError(room_id)                        # unknown room
#         if start >= end:
#             raise ValueError("start must be before end")   # a zero/negative window is meaningless
#         if not self.is_available(room_id, start, end):
#             raise Conflict("overlaps an existing booking")
#         booking_id = f"B{next(self._seq)}"                 # itertools.count → 1,2,3... unique ids
#         self.rooms[room_id].append((start, end, booking_id))   # record it on the room's timeline
#         self.bookings[booking_id] = (room_id, start, end)      # and in the reverse index
#         return booking_id

#     def available_rooms(self, start, end):
#         # LOGIC: filter every room down to the ones free for this window. Iterating a dict yields its
#         # keys IN INSERTION ORDER (Python 3.7+), so results are deterministic (matches add order).
#         return [r for r in self.rooms if self.is_available(r, start, end)]

#     def book_any(self, start, end):
#         # ALLOCATION STRATEGY = first-fit: take the FIRST room that's free, then book it.
#         for r in self.rooms:
#             if start < end and self.is_available(r, start, end):
#                 return (r, self.book(r, start, end))       # reuse book() so all the checks still run
#         raise NoRoomAvailable("no room free for that window")

#     def cancel(self, booking_id):
#         room_id, s, e = self.bookings.pop(booking_id)      # pop → KeyError if unknown (correct)
#         # LOGIC: rebuild the room's timeline WITHOUT this booking. Match by the unique id (b[2]),
#         # not by (start,end) — two bookings could share times across rooms, ids never collide.
#         self.rooms[room_id] = [b for b in self.rooms[room_id] if b[2] != booking_id]
