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


# # The heart of the whole problem — half-open overlap. Keep it a named helper so it reads like
# # the rule you'd say out loud, and so it's testable in isolation (SRP).
# def overlaps(s1, e1, s2, e2):
#     return s1 < e2 and s2 < e1


# class MeetingScheduler:
#     def __init__(self):
#         self.rooms = {}       # room_id -> list of (start, end, booking_id)   (a room's timeline)
#         self.bookings = {}    # booking_id -> (room_id, start, end)           (for cancel)
#         self._seq = itertools.count(1)

#     def add_room(self, room_id):
#         self.rooms[room_id] = []

#     def is_available(self, room_id, start, end):
#         # available == NO existing booking in this room overlaps the requested window.
#         return not any(overlaps(start, end, s, e) for (s, e, _) in self.rooms[room_id])

#     def book(self, room_id, start, end):
#         if room_id not in self.rooms:
#             raise KeyError(room_id)                       # unknown room
#         if start >= end:
#             raise ValueError("start must be before end")  # reject zero/negative windows
#         if not self.is_available(room_id, start, end):
#             raise Conflict("overlaps an existing booking")
#         booking_id = f"B{next(self._seq)}"
#         self.rooms[room_id].append((start, end, booking_id))
#         self.bookings[booking_id] = (room_id, start, end)
#         return booking_id

#     def available_rooms(self, start, end):
#         # insertion order (dict preserves it) → deterministic, matches how rooms were added.
#         return [r for r in self.rooms if self.is_available(r, start, end)]

#     def book_any(self, start, end):
#         # ALLOCATION STRATEGY = first-fit: first room free for the window.
#         for r in self.rooms:
#             if start < end and self.is_available(r, start, end):
#                 return (r, self.book(r, start, end))
#         raise NoRoomAvailable("no room free for that window")

#     def cancel(self, booking_id):
#         room_id, s, e = self.bookings.pop(booking_id)     # KeyError if unknown → correct
#         # drop this booking from the room's timeline (match by id, not by times)
#         self.rooms[room_id] = [b for b in self.rooms[room_id] if b[2] != booking_id]
