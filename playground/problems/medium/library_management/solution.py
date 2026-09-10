"""
LIBRARY MANAGEMENT SYSTEM — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Books have copies; members borrow/return a copy, capped by a per-member limit."
    nouns -> Library, Book (isbn/title/available copies), Member (id + held titles)
    verbs -> add_book, add_member, borrow, return_book, available, borrowed_by

STEP 2 — ENTITIES & RELATIONSHIPS
  Library ◆──── Book        COMPOSITION: the catalog lives and dies with the library.
  Library ◆──── Member       COMPOSITION: membership records are library-managed state.
  Member ───▶ Book (isbn)   ASSOCIATION: a member holds REFERENCES (isbns) to books, not copies
                             of the Book object itself — the library still owns the inventory.
  NO inheritance for book "types" — nothing here varies by book kind (fiction vs reference); a
  book is uniform data (isbn, title, an available-copy counter).

STEP 3 — PATTERN? (what varies?)
  NONE FORCED, on purpose. There's no algorithmic choice to abstract (no pricing/allocation
  strategy, no undo history, no state machine with more than a flat "holds it or doesn't").
  The entire problem IS getting four invariants right on every borrow:
    1. the book exists and has an available copy
    2. the member exists
    3. the member is under their borrow limit
    4. the member doesn't already hold a copy of THIS title
  Reaching for a GoF pattern here would be pure ceremony — the lesson of this problem is
  "recognize when the answer is just clean, well-ordered guard clauses," not "find a pattern."

STEP 4 — SOLID (+ concurrency note)
  SRP   inventory (available-copy counts) and membership (who holds what) are separate dicts
        updated together only inside borrow()/return_book() — no other method touches both.
  OCP   a new borrow RULE (e.g. hold-limit varies by member tier, or a waitlist when copies run
        out) plugs into borrow() as one more guard/branch without touching available()/
        borrowed_by().
  CONCURRENCY  two members racing for the LAST copy of a title: both read available=1, both
        pass the guard, both decrement -> available goes negative (double-lend). Fix: make
        "check available -> decrement" one ATOMIC step (lock per isbn, or a per-book lock) —
        not one global library lock, which would serialize every unrelated borrow/return too.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (stock the shelves, then lend and return) ─────────
#   l = Library(max_borrow=3)
#   l.add_book("isbn1", "Clean Code", copies=2)
#   l.add_book("isbn2", "SICP", copies=1)
#   l.add_member("m1")
#   l.borrow("m1", "isbn1")                    # available copy? yes -> available 2->1, m1 holds it
#   l.available("isbn1")                       # 1
#   l.borrowed_by("m1")                        # ["isbn1"]
#   l.borrow("m1", "isbn1")                    # LibraryError: m1 already holds this title
#   l.return_book("m1", "isbn1")               # frees it: available 1->2, drops from m1's set
#   l.borrowed_by("m1")                        # []
#   # Flow: borrow() is four guard clauses (unknown member/book, no copies, at limit, duplicate
#   # title) THEN a two-field mutation (available count down, member's held-set up); return_book
#   # is the exact mirror.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# class LibraryError(Exception):
#     pass


# class Library:
#     def __init__(self, max_borrow=3):
#         self.max_borrow = max_borrow
#         self.books = {}        # isbn -> {"title": str, "available": int}
#         self.members = {}      # member_id -> set of isbns currently held

#     def add_book(self, isbn, title, copies=1):
#         if isbn in self.books:
#             # LOGIC: re-registering an existing isbn just STACKS more copies onto the pile —
#             # e.g. add_book("isbn2", copies=1) then add_book("isbn2", copies=2) -> available=3.
#             self.books[isbn]["available"] += copies
#         else:
#             self.books[isbn] = {"title": title, "available": copies}

#     def add_member(self, member_id):
#         if member_id in self.members:
#             raise LibraryError(f"member {member_id!r} already exists")
#         self.members[member_id] = set()     # starts holding nothing

#     def borrow(self, member_id, isbn):
#         # LOGIC: guard clauses in the order the contract lists them — unknown identities first
#         # (can't reason about limits/duplicates for entities that don't exist), then the two
#         # "is this allowed" business rules.
#         if member_id not in self.members:
#             raise LibraryError(f"unknown member {member_id!r}")
#         if isbn not in self.books:
#             raise LibraryError(f"unknown book {isbn!r}")
#         book = self.books[isbn]
#         if book["available"] <= 0:
#             raise LibraryError("no copies available")
#         held = self.members[member_id]
#         if len(held) >= self.max_borrow:
#             raise LibraryError("member is at the borrow limit")
#         if isbn in held:
#             # why: a member holding a title already isn't allowed a SECOND copy of the same
#             # title, even if more copies exist — this is a one-book-per-title library.
#             raise LibraryError("member already holds this title")
#         book["available"] -= 1
#         held.add(isbn)

#     def return_book(self, member_id, isbn):
#         if member_id not in self.members:
#             raise LibraryError(f"unknown member {member_id!r}")
#         held = self.members[member_id]
#         if isbn not in held:
#             raise LibraryError("member is not holding this title")
#         held.discard(isbn)
#         self.books[isbn]["available"] += 1

#     def available(self, isbn):
#         if isbn not in self.books:
#             raise LibraryError(f"unknown book {isbn!r}")
#         return self.books[isbn]["available"]

#     def borrowed_by(self, member_id):
#         if member_id not in self.members:
#             raise LibraryError(f"unknown member {member_id!r}")
#         # LOGIC: contract wants a SORTED list — a set has no defined order, so sorted() gives a
#         # deterministic, test-friendly result.
#         return sorted(self.members[member_id])
