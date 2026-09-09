"""
TIC-TAC-TOE — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Two players place marks on a 3x3 grid; first to 3-in-a-row wins; full board = draw."
    nouns -> Player, Board, Symbol(mark), Game   ; verbs -> move, check-win, is-draw
  A "mark" is a closed value set (X/O) → ENUM, not a class.

STEP 2 — ENTITIES & RELATIONSHIPS
  Game ◆──── Board     COMPOSITION: the Board is created and owned by its Game.
  Game o──── Player×2   AGGREGATION: players could exist independently / be passed in.
  Board ───▶ Symbol     ASSOCIATION: cells hold Symbol values.
  NO INHERITANCE. The trap is XPlayer/OPlayer subclasses — players differ only by DATA (their
  symbol), not behaviour → ONE Player class with a `symbol` field.

STEP 3 — PATTERN? Almost nothing varies → NONE needed; forcing a Strategy/State machine here is
  over-engineering (a red flag). We only borrow State LIGHTLY: an explicit GameStatus enum so
  move() can refuse plays after the game ends.

STEP 4 — SOLID
  SRP  Board = cells; Game = turns/rules/win. OCP  N×N generalises with size as a parameter, no
  edits to move()/win. Encapsulate: keep the grid private, expose via place()/get().
────────────────────────────────────────────────────────────────────────────
"""

# ===== SOLUTION (study, then write your own active version) =====

# from enum import Enum
# from typing import Optional


# # WHY an Enum (not "X"/"O" strings): a fixed, closed set; typos like "x"/"0" can't slip in.
# class Symbol(Enum):
#     X = "X"
#     O = "O"


# # The "lightweight State": the game is in exactly one of these at any moment.
# class GameStatus(Enum):
#     IN_PROGRESS = "IN_PROGRESS"
#     WIN = "WIN"
#     DRAW = "DRAW"


# # WHY a custom exception (vs returning False/None): an illegal move must not be silently ignored.
# class InvalidMove(Exception):
#     pass


# # SRP: Board knows ONLY cells — place, read, bounds, fullness. Nothing about turns or winning.
# class Board:
#     def __init__(self, size=3):
#         if size < 3:
#             raise ValueError("size must be >= 3")
#         self.size = size
#         # private grid so storage can change without breaking callers; None = empty cell.
#         self._grid = [[None] * size for _ in range(size)]
#         self._filled = 0                     # count so is_full is O(1), not an O(N^2) rescan

#     def in_bounds(self, r, c):
#         return 0 <= r < self.size and 0 <= c < self.size

#     def is_empty(self, r, c):
#         return self._grid[r][c] is None

#     def place(self, r, c, symbol):
#         self._grid[r][c] = symbol
#         self._filled += 1

#     def get(self, r, c):
#         return self._grid[r][c]

#     @property
#     def is_full(self):
#         return self._filled == self.size * self.size


# # The CONTROLLER: owns the rules (whose turn, is a move legal, did it win/draw).
# class Game:
#     def __init__(self, size=3):
#         self.board = Board(size)             # COMPOSITION: Game creates & owns its Board
#         self._symbols = [Symbol.X, Symbol.O]  # X moves first
#         self._turn = 0                       # index 0/1 into _symbols
#         self._status = GameStatus.IN_PROGRESS  # rich enum kept internally...
#         self.winner: Optional[str] = None

#     @property
#     def status(self):
#         return self._status.value            # ...exposed as the plain string the caller expects

#     @property
#     def current_symbol(self):
#         return self._symbols[self._turn].value

#     def move(self, row, col):
#         # GUARD CLAUSES first: game-over, then bounds, then occupancy (precise failure reason).
#         if self._status != GameStatus.IN_PROGRESS:
#             raise InvalidMove("game is already over")
#         if not self.board.in_bounds(row, col):
#             raise InvalidMove("out of bounds")
#         if not self.board.is_empty(row, col):
#             raise InvalidMove("cell taken")

#         sym = self._symbols[self._turn]
#         self.board.place(row, col, sym)

#         if self._wins(row, col, sym):
#             self._status = GameStatus.WIN
#             self.winner = sym.value
#         elif self.board.is_full:
#             self._status = GameStatus.DRAW
#         else:
#             self._turn = 1 - self._turn      # flip 0<->1: pass the turn

#         return self._status.value

#     def _wins(self, r, c, sym):
#         # EFFICIENCY (SDE-2 signal): only the row/col/diagonals THROUGH (r,c) can complete from
#         # this move → check O(N) cells, not the whole O(N^2) board.
#         n = self.board.size
#         if all(self.board.get(r, j) == sym for j in range(n)):
#             return True
#         if all(self.board.get(i, c) == sym for i in range(n)):
#             return True
#         if r == c and all(self.board.get(i, i) == sym for i in range(n)):
#             return True
#         if r + c == n - 1 and all(self.board.get(i, n - 1 - i) == sym for i in range(n)):
#             return True
#         return False
