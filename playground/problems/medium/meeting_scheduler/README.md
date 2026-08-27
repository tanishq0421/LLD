# Meeting Room Scheduler / Calendar 🟡 Medium

**Format:** machine-coding + OOD · **Asked by:** Microsoft, Google, Amazon, Meta · **Time budget:**
60 min · **Patterns:** none forced — it's about **interval modeling** and clean conflict detection

> An interval-management problem in OOD clothing. The core skill is a correct overlap check
> (`[start, end)` half-open, so back-to-back meetings don't "conflict"), then layering room
> allocation on top. The "minimum rooms needed" follow-up is a classic escalation.

---

## The prompt

> "Design a meeting room scheduler. There are several rooms. A meeting books a room for a time
> interval `[start, end)`. A room can't hold two overlapping meetings. Support booking a specific
> room, checking availability, listing free rooms for an interval, booking any available room, and
> cancelling."

## Clarify before coding

- Are intervals half-open `[start, end)` (so 10:00–11:00 and 11:00–12:00 don't clash)? *"Yes."*
- Time representation? *"Integer minutes/epoch is fine."*
- Zero-length or reversed intervals? *"Reject `start >= end`."*
- Overlapping across rooms is fine — only within a room it's a conflict? *"Correct."*

## Core requirements

1. `add_room(room_id)`.
2. `book(room_id, start, end)` → `booking_id`; raise `Conflict` on overlap, `ValueError` if `start >= end`.
3. `is_available(room_id, start, end)` → bool.
4. `available_rooms(start, end)` → rooms free for that interval (in insertion order).
5. `book_any(start, end)` → `(room_id, booking_id)` for any free room; `NoRoomAvailable` if none.
6. `cancel(booking_id)` frees the slot.

## Design hints

Overlap of `[s1,e1)` and `[s2,e2)` ⟺ `s1 < e2 and s2 < e1`. Keep each room's bookings and check new
requests against them. A linear scan is fine for the base; the interviewer may push you toward an
interval tree / sorted structure for scale. Nouns → `Room`, `Meeting`/`Booking`, `Scheduler`.

## Follow-ups (escalations)

1. **Minimum rooms needed** for a set of meetings (sweep-line / min-heap on end times) — the classic.
2. **Recurring meetings** (daily/weekly) and exceptions.
3. **Attendees & their calendars:** find a slot where all attendees + a room are free.
4. **Scale:** interval tree / segment structure instead of linear scans; time zones.
5. **Concurrency:** two bookings for the last free room at the same instant (booking race).

## Rubric

- **SDE-1:** correct half-open overlap check, per-room booking, availability, cancel.
- **SDE-2:** clean interval abstraction, solves "minimum rooms", and discusses interval-tree scaling
  + the booking-race concurrency angle.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
