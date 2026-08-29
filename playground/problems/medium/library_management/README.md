# Library Management System 🟡 Medium

**Format:** machine-coding + OOD · **Asked by:** Amazon, Adobe, Microsoft, Oracle · **Time budget:**
60 min · **Patterns:** clean entity modeling; Observer (availability), Strategy (fines) as follow-ups

> A bread-and-butter OOD problem. Not pattern-heavy — the signal is clean entities (Book vs BookCopy
> vs Member), correct inventory accounting, and the borrowing invariants (copy limits, no
> double-borrow).

---

## The prompt

> "Design a library system. Books have multiple copies. Members borrow and return copies. A member
> can hold at most a fixed number of books at a time, and can't borrow a title they already hold or a
> title with no copies available. Track how many copies are available and what each member holds."

## Clarify before coding

- Distinguish a Book (title/ISBN) from a physical copy? *"Track copy counts per ISBN; a specific-copy
  model is a nice extension."*
- Per-member borrow limit? *"Yes — say 3."*
- Can a member borrow two copies of the same title? *"No — one copy per title per member."*
- Due dates / fines? *"Out of scope for the base; a follow-up."*

## Core requirements

1. `add_book(isbn, title, copies=1)` (stack copies if it already exists); `add_member(member_id)`.
2. `borrow(member_id, isbn)` — reject: unknown member/book, no available copies, member at borrow
   limit, or member already holds this title (`LibraryError`). Decrement availability.
3. `return_book(member_id, isbn)` — reject if the member isn't holding it. Increment availability.
4. `available(isbn)` → available copies; `borrowed_by(member_id)` → sorted list of held ISBNs.

## Design hints

Nouns → `Book`(title + copy counts), `Member`(held set), `Library`. Keep a per-member set of held
ISBNs for O(1) limit + double-borrow checks. Availability is a simple counter per ISBN. No pattern
required — resist adding one.

## Follow-ups (escalations)

1. **Due dates + fines** (inject a clock; fines as a **Strategy**).
2. **Reservations/holds:** waitlist for an out-of-stock title, notify on return (**Observer**).
3. **Specific-copy tracking** (barcodes), multiple branches/locations.
4. **Search** by title/author/genre (index structures).
5. **Concurrency:** two members grabbing the last copy at once.

## Rubric

- **SDE-1:** correct borrow/return accounting, all invariants (limit, no-double-borrow, availability).
- **SDE-2:** clean Book/Copy/Member separation, fines/holds via Strategy/Observer, and a concurrency
  story for the last-copy race.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
