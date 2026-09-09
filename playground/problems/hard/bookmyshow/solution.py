"""
BOOKMYSHOW / SEAT BOOKING — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

WHY THIS ONE FOR DISTRICT (and Blinkit-family): District is Zomato's events/movies app — its core
is booking specific seats for a show. The whole difficulty is the concurrency guarantee: a seat
can be sold to at most ONE person, ever, even when two users tap "book" at the same instant.

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES
  "A show has seats; users book one or more; a seat goes to one person; booking N seats is
   all-or-nothing; cancel frees seats."
    nouns -> BookingService, Show, Seat, Booking ; verbs -> add_show, available, book, cancel

STEP 2 — ENTITIES & RELATIONSHIPS
  Service ◆──── Show          COMPOSITION: the service owns shows.
  Show ◆──── Seat             COMPOSITION: seats belong to their show (here: a seat_id -> booked?
                              map per show — a seat is tiny state, so a bool per id is enough).
  Booking ───▶ Show, Seats    ASSOCIATION: a booking REFERENCES the show + the seat ids it holds.
  Seat status is a mini STATE (AVAILABLE/BOOKED; HELD appears in the hold-timeout follow-up).

STEP 3 — PATTERN? The base needs NO GoF pattern — the content is CONCURRENCY CORRECTNESS, not
  machinery. (Follow-ups invite Observer for "notify waitlist when a seat frees", Strategy for
  pricing/seat-class. Mention them; don't build them unasked.)

  ★ ALL-OR-NOTHING: booking [A5, A6] must either take BOTH or take NEITHER. So the flow is
  CHECK all requested seats are free  →  then MARK them all. Never mark seat-by-seat (you'd
  half-book and leave junk to roll back).

STEP 4 — CONCURRENCY (THE interview point — rehearse this out loud)
  Race: two users both call book(show, ["A5"]). Both READ "A5 is free", both WRITE "booked" →
  double-sold. The check and the mark must be ONE atomic critical section.
    • Simplest correct: a lock PER SHOW around check-then-mark (used below).
    • Better throughput: lock PER SEAT (or an optimistic compare-and-set on each seat's status,
      retry on conflict) so unrelated seats don't serialise. Say WHY: one GLOBAL lock over the
      whole service serialises every booking in the system and destroys throughput.
    • DB analogy: `SELECT ... FOR UPDATE` on the seat rows, or a UNIQUE constraint on
      (show_id, seat_id) in a bookings table that makes the DB reject the second insert.
  Follow-up: HOLD seats for N minutes during payment (a HELD state + a reaper that auto-releases).
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (pick seats, book atomically) ─────────────────────
#   svc = BookingService()
#   svc.add_show("S1", ["A1", "A2", "A3"])     # all AVAILABLE; one Lock created for show S1
#   svc.available_seats("S1")                  # ["A1", "A2", "A3"]
#   bk = svc.book("S1", ["A1", "A2"], "u1")    # under S1's lock: both free? yes → mark BOTH → "BK1"
#   svc.book("S1", ["A2"], "u2")               # A2 already booked → SeatUnavailable (nothing half-booked)
#   svc.available_seats("S1")                  # ["A3"]
#   svc.cancel(bk)                             # under the lock → frees A1, A2 again
#   # Flow:  two users → book() serialised by the PER-SHOW lock → check-ALL-then-mark-ALL → no double-sell.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import threading
# import itertools


# class SeatUnavailable(Exception):
#     pass


# class BookingService:
#     def __init__(self):
#         self.shows = {}      # show_id -> {seat_id: booked?}   (False = AVAILABLE, True = BOOKED)
#         self.locks = {}      # show_id -> Lock   (one lock PER show = fine-grained, not one global lock)
#         self.bookings = {}   # booking_id -> {"show_id", "user_id", "seats"}
#         self._seq = itertools.count(1)

#     def add_show(self, show_id, seat_ids):
#         # every seat starts False (available); dict-comprehension builds {A1:False, A2:False, ...}.
#         self.shows[show_id] = {s: False for s in seat_ids}
#         self.locks[show_id] = threading.Lock()          # this show's own lock

#     def available_seats(self, show_id):
#         seats = self.shows[show_id]                     # KeyError if unknown show → correct
#         # keep only the seats whose value is False (not booked); sorted() for a stable, readable list.
#         return sorted(s for s, booked in seats.items() if not booked)

#     def book(self, show_id, seat_ids, user_id):
#         seats = self.shows[show_id]                     # KeyError if unknown show
#         # validate seat ids BEFORE taking the lock — cheap checks shouldn't hold the lock.
#         for s in seat_ids:
#             if s not in seats:
#                 raise KeyError(s)                        # unknown seat id
#         # CRITICAL SECTION. Only one thread per show is inside here at a time, so the "are they all
#         # free?" check and the "mark them all" write happen as ONE indivisible step — no other
#         # booking can slip between them and grab the same seat.
#         with self.locks[show_id]:
#             # ALL-OR-NOTHING check: any(...) is True if EVEN ONE requested seat is already booked.
#             if any(seats[s] for s in seat_ids):
#                 raise SeatUnavailable("one or more seats already booked")
#             # only now, when we KNOW all are free, do we mark them — so we never half-book.
#             for s in seat_ids:
#                 seats[s] = True
#             booking_id = f"BK{next(self._seq)}"
#             self.bookings[booking_id] = {"show_id": show_id, "user_id": user_id,
#                                          "seats": list(seat_ids)}
#             return booking_id

#     def cancel(self, booking_id):
#         bk = self.bookings.pop(booking_id)              # pop → KeyError if unknown booking
#         seats = self.shows[bk["show_id"]]
#         # flip the seats back to available, under the same per-show lock (a concurrent booking must
#         # not read a half-updated seat map).
#         with self.locks[bk["show_id"]]:
#             for s in bk["seats"]:
#                 seats[s] = False

#     def get_booking(self, booking_id):
#         return self.bookings[booking_id]                # KeyError if unknown
