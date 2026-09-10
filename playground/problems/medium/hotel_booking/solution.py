"""
HOTEL BOOKING — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Rooms of a type; book [check_in, check_out); no overlap per room; search by type; book any
  free room of a type; cancel."
    nouns -> Hotel, Room(type), Reservation ; verbs -> add_room, is_available, find_available,
    book, book_any, cancel

STEP 2 — ENTITIES & RELATIONSHIPS
  Hotel ◆──── Room             COMPOSITION: the hotel owns its rooms (created via add_room, die
                               with the hotel).
  Room ◆──── Reservation        COMPOSITION: a reservation is a slot INSIDE a room's own calendar;
                               it has no meaning detached from that room.
  Reservation ───▶ Room        ASSOCIATION: the reverse index (booking_id -> room_id) references
                               the room without owning it — needed so cancel() is O(1) to find.
  Room TYPE is closed-set DATA ("standard"/"deluxe"/"suite"), not a subclass — rooms differ by a
  label used for search filtering, not by behaviour. NO inheritance.

STEP 3 — PATTERN? (what varies?)
  Same shape as the meeting scheduler, one dimension richer: dates instead of hours, PLUS a room
  TYPE to filter/search by. No GoF pattern needed for the base (resist over-engineering) — the
  real content is the interval-overlap rule, applied per room, plus a room-type INDEX so
  find_available/book_any don't have to scan every room in the hotel.
  book_any is a light allocation Strategy (first-fit by insertion order); name the seam — a
  follow-up could rank by price/floor/view instead.

  ★ THE ONE RULE TO MEMORISE — half-open ranges [check_in, check_out):
      two ranges overlap  ⟺  in1 < out2  AND  in2 < out1
    A checkout on day 12 and a new check-in on day 12 DON'T clash — the room turns over same day.

STEP 4 — SOLID + SCALE + CONCURRENCY
  SRP  the overlap test is one tiny function; each room's booking list is its own timeline; Hotel
       coordinates the type index and the reverse booking lookup.
  OCP  a new allocation rule (book_any) or a new search rank = a new Strategy, not edits to book().
  SCALE  linear scan per room is fine to state; "at scale, an interval tree per room, or a
       per-day availability bitmap indexed by room type, for O(log n) search."
  CONCURRENCY  two guests book the last free deluxe room for overlapping dates at the same
       instant → both read "available", both insert → double-booking. Fix: lock the
       check-then-insert as ONE atomic step, scoped per ROOM (not a hotel-wide lock, which would
       serialise every booking across every room type and kill throughput).
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (search, book, clash, cancel) ──────────────────────
#   h = Hotel()
#   h.add_room("101", "standard"); h.add_room("102", "standard"); h.add_room("201", "deluxe")
#   h.book("101", "alice", 10, 12)              # checks dates, no overlap -> insert -> "BK1"
#   h.is_available("101", 11, 13)               # False (11 falls inside [10,12))
#   h.is_available("101", 12, 14)               # True  (checkout day 12 frees the room)
#   h.find_available("standard", 10, 12)        # ["102"]  (101 is busy in that window)
#   room, bid = h.book_any("standard", 10, 12)  # first free standard room, in insertion order -> "102"
#   h.book_any("deluxe", 10, 12)                # NoRoomAvailable if "201" is already taken there
#   h.cancel("BK1")                             # frees [10,12) on 101 again
#   # Flow:  guest -> Hotel.find_available/book_any (scans that TYPE's room list) -> Hotel.book
#   # (scans THAT room's reservations for overlap) -> insert + reverse-index for cancel.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import itertools


# class Conflict(Exception):
#     pass


# class NoRoomAvailable(Exception):
#     pass


# # THE HEART OF THE PROBLEM — identical shape to the meeting scheduler's overlap rule, now over
# # DAY NUMBERS instead of hours. Two ranges [in1,out1) and [in2,out2) MISS each other only when one
# # ends at/before the other starts (out1<=in2 or out2<=in1); overlap is the negation of that:
# #   overlap == NOT(out1<=in2 or out2<=in1) == (out1>in2) and (out2>in1) == (in1<out2) and (in2<out1)
# # Example: [10,12) vs [12,14) -> in1<out2 (10<14 T) and in2<out1 (12<12 F) -> False -> no clash
# # (back-to-back checkout/check-in on the same day 12 is allowed).
# def overlaps(in1, out1, in2, out2):
#     return in1 < out2 and in2 < out1


# class Hotel:
#     def __init__(self):
#         self.room_type = {}         # room_id -> room_type                (what a room IS)
#         self.bookings_by_room = {}  # room_id -> [(check_in, check_out, booking_id), ...]
#         # LOGIC: an INDEX by type so find_available/book_any don't scan every room in the hotel,
#         # only the ones of the requested type. List (not set) preserves insertion order, which
#         # the contract requires for find_available's return order and book_any's first-fit.
#         self.rooms_by_type = {}     # room_type -> [room_id, ...] in add_room order
#         self.bookings = {}          # booking_id -> (room_id, check_in, check_out)  (reverse index)
#         self._seq = itertools.count(1)

#     def add_room(self, room_id, room_type):
#         self.room_type[room_id] = room_type
#         self.bookings_by_room[room_id] = []                       # empty calendar to start
#         self.rooms_by_type.setdefault(room_type, []).append(room_id)

#     def is_available(self, room_id, check_in, check_out):
#         # LOGIC: available == this window overlaps NONE of the room's existing reservations.
#         # `any(...)` short-circuits True on the first clash; `not any(...)` flips that to "free".
#         return not any(
#             overlaps(check_in, check_out, s, e)
#             for (s, e, _) in self.bookings_by_room[room_id]
#         )

#     def find_available(self, room_type, check_in, check_out):
#         # LOGIC: filter THAT type's room list (insertion order preserved by the list) down to the
#         # ones free for this window. `.get(type, [])` -> an unknown/empty type just yields [].
#         return [
#             r for r in self.rooms_by_type.get(room_type, [])
#             if self.is_available(r, check_in, check_out)
#         ]

#     def book(self, room_id, guest, check_in, check_out):
#         if check_in >= check_out:
#             raise ValueError("check_in must be before check_out")   # a zero/negative stay is meaningless
#         if room_id not in self.room_type:
#             raise KeyError(room_id)                                  # unknown room
#         if not self.is_available(room_id, check_in, check_out):
#             raise Conflict("overlaps an existing booking")
#         booking_id = f"BK{next(self._seq)}"
#         # --- check-then-insert: THIS is the critical section a concurrency follow-up must lock,
#         # scoped to this ROOM so bookings on other rooms (even other rooms of the same type)
#         # aren't serialised behind it. ---
#         self.bookings_by_room[room_id].append((check_in, check_out, booking_id))
#         self.bookings[booking_id] = (room_id, check_in, check_out)
#         return booking_id

#     def book_any(self, room_type, check_in, check_out):
#         # ALLOCATION STRATEGY = first-fit over rooms of this type, in insertion order.
#         # book_any doesn't take a guest name in the contract, so we pass a generic placeholder —
#         # a real system would thread the caller's guest id through instead.
#         for room_id in self.rooms_by_type.get(room_type, []):
#             if self.is_available(room_id, check_in, check_out):
#                 # reuse book() so the date/room validation stays in ONE place (no duplicated logic).
#                 return room_id, self.book(room_id, "guest", check_in, check_out)
#         raise NoRoomAvailable("no room of that type free for those dates")

#     def cancel(self, booking_id):
#         room_id, check_in, check_out = self.bookings.pop(booking_id)   # KeyError if unknown (correct)
#         # LOGIC: rebuild that room's calendar WITHOUT this booking, matched by its unique id
#         # (not by dates — two different guests could in principle share identical ranges across
#         # cancelled/rebooked history; the id never collides).
#         self.bookings_by_room[room_id] = [
#             b for b in self.bookings_by_room[room_id] if b[2] != booking_id
#         ]
