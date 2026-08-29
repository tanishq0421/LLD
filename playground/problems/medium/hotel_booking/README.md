# Hotel Booking System 🟡 Medium

**Format:** machine-coding + OOD · **Asked by:** Uber, Lyft, Airbnb, Booking.com, Amazon · **Time
budget:** 60 min · **Patterns:** interval modeling; Strategy (pricing), Observer (availability) as
follow-ups

> Like the meeting scheduler, but over **date ranges** and with **room types**: guests want *"any
> deluxe room for these nights."* The core is availability search + no double-booking per room; the
> pricing/overbooking follow-ups push it toward a real booking engine.

---

## The prompt

> "Design a hotel booking system. The hotel has rooms of different types (standard, deluxe, suite). A
> guest books a specific room for a date range `[check_in, check_out)`; a room can't be double-booked
> for overlapping dates. Support searching for available rooms of a type for a date range, and
> booking any available room of a type. Support cancellation."

## Clarify before coding

- Half-open dates so a checkout day frees the room for a new check-in? *"Yes — `[in, out)`."*
- Search by room type? *"Yes — 'any deluxe for these nights.'"*
- Dates representation? *"Integer day numbers are fine."*
- Overbooking allowed? *"No for the base; it's a follow-up."*

## Core requirements

1. `add_room(room_id, room_type)`.
2. `is_available(room_id, check_in, check_out)` and `find_available(room_type, check_in, check_out)`
   (room ids of that type free for the range, in insertion order).
3. `book(room_id, guest, check_in, check_out)` → `booking_id`; `Conflict` on overlap, `ValueError`
   if `check_in >= check_out`, `KeyError` if the room is unknown.
4. `book_any(room_type, check_in, check_out)` → `(room_id, booking_id)`; `NoRoomAvailable` if none.
5. `cancel(booking_id)` frees the dates.

## Design hints

Overlap of `[in1,out1)` and `[in2,out2)` ⟺ `in1 < out2 and in2 < out1` — same half-open rule as the
meeting scheduler, now per room and filtered by type. Keep each room's bookings and an index by type.
Nouns → `Room`(type), `Reservation`, `Hotel`. A linear scan is fine for the base; interval trees are
the scaling follow-up.

## Follow-ups (escalations)

1. **Dynamic pricing** by season/occupancy (**Strategy**); minimum-stay rules.
2. **Overbooking policy** (book N% above capacity) and waitlists (**Observer** on cancellations).
3. **Search ranking** (price, floor, view); amenities filters.
4. **Scale:** interval trees / per-day availability bitmaps instead of scans.
5. **Concurrency:** two guests booking the last deluxe room for overlapping dates.

## Rubric

- **SDE-1:** correct half-open overlap per room, type-filtered availability, book/cancel accounting.
- **SDE-2:** clean type index, pricing/overbooking as additions, and a concurrency + scaling story.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
