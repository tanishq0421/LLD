# BookMyShow (Movie Ticket Booking) 🔴 Hard

**Format:** machine-coding + concurrency · **Asked by:** widely; the "two users book the same seat"
follow-up is near-universal · **Time budget:** 75–90 min · **Patterns:** State (seat/booking),
Observer (availability), Strategy (pricing/seat-selection)

> The base modeling is medium; what makes it **hard** is the escalation everyone gets:
> **prevent double-booking under concurrency**. That single-seat race is the whole SDE-2 test.

---

## The prompt

> "Design a movie ticket booking system. A show has a set of seats. Users browse available seats
> and book one or more of them. A seat can be booked by only one user. Booking multiple seats is
> all-or-nothing. Users can cancel a booking, which frees the seats."

## Clarify before coding

- Scope: full theatre/city/movie catalog, or just show → seats → booking? *"Focus on show, seats, booking. Catalog is out of scope."*
- Booking multiple seats: all-or-nothing, or partial? *"All-or-nothing."*
- Do we hold seats during payment, or book instantly? *"Instant for the base; seat-hold-with-timeout is a follow-up."*
- What must never happen? *"Two confirmed bookings for the same seat. Ever."*

## Core requirements

1. `add_show(show_id, seat_ids)` — register a show and its seats.
2. `available_seats(show_id)` — seats not currently booked.
3. `book(show_id, seat_ids, user_id)` — book **all** requested seats atomically; return a
   `booking_id`. If **any** requested seat is unavailable, book **none** and raise `SeatUnavailable`.
4. `cancel(booking_id)` — free that booking's seats.
5. Unknown show/seat/booking → error.

## The concurrency requirement (this is the point)

Two users call `book(show, ["A5"], ...)` at the same instant. A naive implementation reads
"A5 available → true" in both threads, then both write "booked" → **double-booked**. You must
guarantee **at most one** succeeds. Options to discuss:
- **Pessimistic:** a lock per show (or per seat) around the check-and-set.
- **Optimistic:** compare-and-swap on seat version/status; retry on conflict.
- **DB analogy:** `SELECT ... FOR UPDATE`, or a unique constraint on `(show, seat)` in a bookings table.

Fine-grained (per-seat/per-show) locking beats one global lock, which serializes every booking in
the system.

## Follow-ups (escalations)

1. **Seat hold with timeout:** `hold(seats)` reserves for N minutes during payment; auto-release on
   expiry; `confirm(hold_id)` finalizes. Now seats have a `HELD` state (State pattern) + a reaper.
2. **Pricing strategy:** different seat classes (silver/gold/recliner), dynamic/surge pricing.
3. **Availability notifications:** notify waitlisted users when a seat frees up (**Observer**).
4. **Scale:** many shows across many servers → move the atomic seat claim to the database/Redis.

## Rubric

- **SDE-1:** correct all-or-nothing booking, cancel frees seats, guards for unknown ids.
- **SDE-2:** precisely names the check-then-act race, implements a correct **fine-grained** lock (or
  optimistic CAS), and explains hold-with-timeout + the distributed version.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
The concurrency stress test is **skipped by default** — enable it once your `book` is thread-safe.
