"""
CHESS (core movement) — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "A board holds pieces on squares; a piece belongs to a color and a type; a move is legal
   only if that piece TYPE allows that shape, the path is clear (for sliders), and the
   destination isn't a same-color piece; a capture removes the enemy piece; turns alternate."
    nouns -> ChessGame, board, Square, Piece (color+type) ; verbs -> piece_at, move
  Square is just a 2-char string key ("e2") — giving it a class would be ceremony for a
  coordinate pair. Piece type, however, is NOT a closed set of interchangeable data (like
  parking Vehicle types) — each type has genuinely different MOVEMENT BEHAVIOR. That's the
  signal for real polymorphism instead of a flat lookup table (see STEP 3).

STEP 2 — ENTITIES & RELATIONSHIPS
  ChessGame ◆──── board (squares -> piece codes)   COMPOSITION: the game owns board state.
  ChessGame ───▶ MoveRule (per piece type)          ASSOCIATION via a FACTORY dict: the game
                                                     asks "who validates a 'N' move?" and gets
                                                     back the one shared KnightRule instance.
  Piece "wP"/"bK" etc. is DATA (2-char code: color + type) — no Piece class needed; the RULE
  objects (one per type letter) hold the behavior, not the piece codes themselves.

STEP 3 — PATTERN? (what varies?)  FACTORY + POLYMORPHIC PER-PIECE MOVE RULES
  What varies is "is this shape legal for THIS piece type" — six genuinely different answers
  (pawn's forward-only-with-a-diagonal-capture-exception is nothing like a knight's L-jump).
  Cramming all six into one giant if/elif on piece type inside move() is exactly the kind of
  method OCP warns about: every new piece type (or every variant-rules follow-up: Fischer
  Random, a "wizard" fairy piece, ...) means editing that one already-huge function.
  Instead: each piece type gets its OWN small class with the SAME method name (`legal(...)`)
  but type-specific logic — polymorphism. A dict {"P": PawnRule(), "N": KnightRule(), ...} is
  the FACTORY: given a type letter, it hands back the right validator object. move() then
  just does `RULES[piece_type].legal(...)` — it never needs to know how many piece types
  exist or how any of them individually work. Adding a 7th fairy piece = one new class + one
  new dict entry; move() doesn't change (OCP).
  Sliding pieces (B/R/Q) additionally share a "walk the straight/diagonal line, must be all
  empty until the last square" path-clear check — factored into one shared helper so Bishop/
  Rook/Queen don't triplicate it (DRY; Queen's rule is literally "diagonal-shape OR
  straight-shape, then path-clear" — composition of the other two's shape checks).

STEP 4 — SOLID
  SRP  Each Rule class answers exactly one question: "is this shape legal for MY piece type,
       ignoring whose turn it is / what's on the destination" (those are move()'s job, checked
       once, generically, for every piece — no rule repeats them).
  OCP  New piece type / variant movement rule -> new Rule class + one factory entry. move()'s
       flow (find piece -> check turn -> check same-color target -> ask the rule -> apply)
       never changes.
  LSP  Every Rule is substitutable: move() calls `.legal(board, color, frm, to)` on whichever
       one the factory returns, never caring which concrete class it got back.
  Concurrency note: a single ChessGame models ONE game between two turns; it isn't meant to be
  shared across threads. If it were (e.g. a server holding many live games), the fix is one
  lock PER GAME (not one global lock across all games) around the read-validate-write of a
  single move — the same "small atomic critical section" idea as the parking/booking systems.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (opening moves, a capture, an illegal attempt) ────
#   g = ChessGame()                      # standard setup, white to move
#   g.piece_at("e2")                     # "wP"
#   g.move("e2", "e4")                   # pawn rule: dx=0, dy=+2, on start rank, path+dest empty
#                                         #   -> legal -> board updates, turn becomes "black"
#   g.move("d7", "d5")                   # black pawn double-step
#   g.move("e4", "d5")                   # pawn rule: dx=-1, dy=+1 (diagonal), dest has enemy
#                                         #   piece -> legal CAPTURE -> bP at d5 removed, wP moves in
#   g.move("e2", "e3")                   # RULES["P"].legal(...) sees e2 empty now (no piece)
#                                         #   -> move() raises IllegalMove BEFORE even asking the
#                                         #   rule, since piece_at(frm) is None
#   # Flow: move() looks up the piece -> confirms it's the mover's color -> confirms the target
#   # isn't own-color -> looks the piece TYPE up in the RULES factory -> that rule (polymorphic,
#   # e.g. sliders also walk the path) says legal/illegal -> on legal, board mutates and turn flips.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====


# class IllegalMove(Exception):
#     pass


# def _parse(square):
#     # LOGIC: "e2" -> col=4 (e is the 5th file, 0-indexed), row=1 (rank 2, 0-indexed).
#     # Keeping board math in (col, row) integers makes every shape check a plain number check.
#     col = ord(square[0]) - ord("a")
#     row = int(square[1]) - 1
#     return col, row


# def _fmt(coord):
#     # LOGIC: inverse of _parse — (4, 1) -> "e2". Needed to re-key the board dict and to walk
#     # intermediate squares for the sliding-piece path-clear check.
#     col, row = coord
#     return chr(ord("a") + col) + str(row + 1)


# def _sign(n):
#     return (n > 0) - (n < 0)   # -1, 0, or 1 — the direction of travel along one axis


# def _path_clear(board, frm, to):
#     # LOGIC: shared by Bishop/Rook/Queen. Step one square at a time from frm TOWARD to (using
#     # the unit direction on each axis) and stop just BEFORE to — every one of those squares
#     # must be empty, or something is in the way. e.g. a1->a4: step (0,1), checks a2, a3 (not a4
#     # itself — a4's own occupancy is handled separately by the "not same-color target" rule).
#     fc, fr = frm
#     tc, tr = to
#     dc, dr = _sign(tc - fc), _sign(tr - fr)
#     c, r = fc + dc, fr + dr
#     while (c, r) != (tc, tr):
#         if board.get(_fmt((c, r))) is not None:
#             return False   # something occupies a square we must pass through
#         c, r = c + dc, r + dr
#     return True


# def _is_diagonal(dx, dy):
#     return dx != 0 and abs(dx) == abs(dy)


# def _is_straight(dx, dy):
#     return (dx == 0) != (dy == 0)   # exactly one axis moves, the other stays put


# class PawnRule:
#     def legal(self, board, color, frm, to):
#         fc, fr = frm
#         tc, tr = to
#         dx, dy = tc - fc, tr - fr
#         # LOGIC: white moves UP the board (increasing rank -> +1 row), black moves DOWN (-1).
#         direction = 1 if color == "w" else -1
#         start_row = 1 if color == "w" else 6   # rank 2 for white, rank 7 for black (0-indexed)
#         dest = board.get(_fmt(to))
#         if dx == 0:
#             # Straight move: only ever onto an EMPTY square (pawns can't capture forward).
#             if dest is not None:
#                 return False
#             if dy == direction:
#                 return True                                    # single step
#             if dy == 2 * direction and fr == start_row:
#                 mid = _fmt((fc, fr + direction))                # the square hopped over
#                 return board.get(mid) is None                   # double step needs BOTH clear
#             return False
#         if abs(dx) == 1 and dy == direction:
#             # Diagonal move: only ever onto an ENEMY piece (this base scope has no en passant).
#             return dest is not None and dest[0] != color
#         return False


# class KnightRule:
#     _DELTAS = {(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)}

#     def legal(self, board, color, frm, to):
#         dx, dy = to[0] - frm[0], to[1] - frm[1]
#         return (dx, dy) in self._DELTAS   # L-shape: knights jump, so no path-clear check at all


# class BishopRule:
#     def legal(self, board, color, frm, to):
#         dx, dy = to[0] - frm[0], to[1] - frm[1]
#         return _is_diagonal(dx, dy) and _path_clear(board, frm, to)


# class RookRule:
#     def legal(self, board, color, frm, to):
#         dx, dy = to[0] - frm[0], to[1] - frm[1]
#         return _is_straight(dx, dy) and _path_clear(board, frm, to)


# class QueenRule:
#     def legal(self, board, color, frm, to):
#         # LOGIC: a queen is literally "rook or bishop" — compose the two shape checks instead
#         # of re-deriving the math a third time.
#         dx, dy = to[0] - frm[0], to[1] - frm[1]
#         return (_is_diagonal(dx, dy) or _is_straight(dx, dy)) and _path_clear(board, frm, to)


# class KingRule:
#     def legal(self, board, color, frm, to):
#         dx, dy = to[0] - frm[0], to[1] - frm[1]
#         return max(abs(dx), abs(dy)) == 1   # exactly one square, any direction (no castling here)


# # FACTORY: piece-type letter -> the one shared rule OBJECT that knows how to validate ITS OWN
# # kind of move. move() below never branches on piece type itself — it just asks whichever rule
# # the factory hands back. Adding a new piece type is "write a class, add a dict line" (OCP).
# RULES = {
#     "P": PawnRule(),
#     "N": KnightRule(),
#     "B": BishopRule(),
#     "R": RookRule(),
#     "Q": QueenRule(),
#     "K": KingRule(),
# }


# class ChessGame:
#     def __init__(self):
#         self.board = {}
#         # LOGIC: back rank order by file a..h is fixed in real chess: Rook Knight Bishop Queen
#         # King Bishop Knight Rook. Build both colors' back ranks and pawn ranks from one loop.
#         back_rank = "RNBQKBNR"
#         for col in range(8):
#             self.board[_fmt((col, 0))] = "w" + back_rank[col]   # rank 1: white pieces
#             self.board[_fmt((col, 1))] = "wP"                    # rank 2: white pawns
#             self.board[_fmt((col, 6))] = "bP"                    # rank 7: black pawns
#             self.board[_fmt((col, 7))] = "b" + back_rank[col]    # rank 8: black pieces
#         self._turn = "white"

#     @property
#     def turn(self):
#         return self._turn

#     def piece_at(self, square):
#         return self.board.get(square)   # None if the square is empty

#     def move(self, frm, to):
#         piece = self.board.get(frm)
#         if piece is None:
#             raise IllegalMove(f"no piece at {frm}")
#         color, ptype = piece[0], piece[1]
#         expected_color = "w" if self._turn == "white" else "b"
#         if color != expected_color:
#             raise IllegalMove(f"it is {self._turn}'s move")
#         dest_piece = self.board.get(to)
#         if dest_piece is not None and dest_piece[0] == color:
#             raise IllegalMove("cannot capture your own piece")
#         # LOGIC: this is the polymorphic dispatch from STEP 3 — RULES[ptype] resolves to the
#         # ONE class that knows this piece type's shape (and, for sliders, its path-clear check).
#         rule = RULES[ptype]
#         if not rule.legal(self.board, color, _parse(frm), _parse(to)):
#             raise IllegalMove(f"illegal move for {piece}: {frm}->{to}")
#         # Legal: apply it. A capture is implicit — assigning over `to` discards whatever was there.
#         del self.board[frm]
#         self.board[to] = piece
#         self._turn = "black" if self._turn == "white" else "white"
