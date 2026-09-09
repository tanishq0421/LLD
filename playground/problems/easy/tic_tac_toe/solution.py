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

# ─── STEP 5 · HOW IT'S USED (object flow / a run-through) ─────────────────────
#   g = Game()                 # __init__ CREATES the Board (composition) + symbols [X, O]; X to move.
#                              #   alt design: board = Board(); Game(board)  → board INJECTED = aggregation/DIP
#   g.current_symbol           # "X"  (whose turn it is)
#   g.move(0, 0)               # X→(0,0): Game validates → Board.place → _wins? no → flip turn → "IN_PROGRESS"
#   g.move(1, 0)               # O→(1,0)
#   g.move(0, 1)               # X→(0,1)
#   g.move(1, 1)               # O→(1,1)
#   g.move(0, 2)               # X completes the top row → _wins True → status "WIN", g.winner == "X"
#   # A driver (or the test harness) just loops: read current_symbol, call move(r,c), read the status.
#   # Per move the control flows:  caller → Game.move → Board.place/get → Game decides win/draw/next-turn.
# ─────────────────────────────────────────────────────────────────────────────

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
#         # LOGIC: a size×size grid of cells, all empty (None). `[[None]*size for _ in range(size)]`
#         # builds a FRESH inner list per row — do NOT write [[None]*size]*size, that repeats the
#         # SAME row object size times, so editing one cell would change the whole column.
#         self._grid = [[None] * size for _ in range(size)]
#         # LOGIC: track how many cells are filled so is_full is O(1). We increment on each place()
#         # instead of scanning all N² cells every time we want to know "is the board full?".
#         self._filled = 0

#     def in_bounds(self, r, c):
#         # LOGIC: valid indices are 0..size-1 on both axes. `0 <= r < size` is the Pythonic range check.
#         return 0 <= r < self.size and 0 <= c < self.size

#     def is_empty(self, r, c):
#         return self._grid[r][c] is None          # None means "no mark here yet"

#     def place(self, r, c, symbol):
#         self._grid[r][c] = symbol
#         self._filled += 1                         # keep the O(1) fullness counter in sync

#     def get(self, r, c):
#         return self._grid[r][c]

#     @property
#     def is_full(self):
#         # LOGIC: a size×size board has size*size cells; if we've filled them all, it's full.
#         return self._filled == self.size * self.size


# # The CONTROLLER: owns the rules (whose turn, is a move legal, did it win/draw).
# class Game:
#     def __init__(self, size=3):
#         self.board = Board(size)                  # COMPOSITION: Game creates & owns its Board
#         self._symbols = [Symbol.X, Symbol.O]      # index 0 = X (moves first), index 1 = O
#         self._turn = 0                            # whose turn: an index into _symbols
#         self._status = GameStatus.IN_PROGRESS     # rich enum kept internally...
#         self.winner: Optional[str] = None

#     @property
#     def status(self):
#         return self._status.value                 # ...exposed as the plain string the caller expects

#     @property
#     def current_symbol(self):
#         # LOGIC: _turn is 0 or 1, so this reads the current player's Symbol and returns "X"/"O".
#         return self._symbols[self._turn].value

#     def move(self, row, col):
#         # GUARD CLAUSES first: reject in order game-over → out-of-bounds → occupied, so the raised
#         # message names the FIRST real reason. Guards up top keep the happy path flat/unindented.
#         if self._status != GameStatus.IN_PROGRESS:
#             raise InvalidMove("game is already over")
#         if not self.board.in_bounds(row, col):
#             raise InvalidMove("out of bounds")
#         if not self.board.is_empty(row, col):
#             raise InvalidMove("cell taken")

#         sym = self._symbols[self._turn]           # the mark we're about to place
#         self.board.place(row, col, sym)

#         # DECIDE the resulting status from THIS move:
#         if self._wins(row, col, sym):
#             self._status = GameStatus.WIN
#             self.winner = sym.value
#         elif self.board.is_full:                  # board full AND nobody won → draw
#             self._status = GameStatus.DRAW
#         else:
#             # LOGIC: toggle turn between 0 and 1. 1-0 = 1, 1-1 = 0, so it flips each call. (Cleaner
#             # than an if/else; for >2 players you'd use (self._turn + 1) % num_players instead.)
#             self._turn = 1 - self._turn

#         return self._status.value

#     def _wins(self, r, c, sym):
#         # KEY INSIGHT: the move at (r,c) can only COMPLETE a line that PASSES THROUGH (r,c). There
#         # are at most 4 such lines — this cell's row, its column, and (only if it sits on them) the
#         # two diagonals. So we check 4 lines of N cells = O(N), never the whole O(N²) board.
#         n = self.board.size
#         # row r: are all N cells in this row == sym?  `all(...)` is True only if every check passes.
#         if all(self.board.get(r, j) == sym for j in range(n)):
#             return True
#         # column c: same, walking down the rows at fixed column c.
#         if all(self.board.get(i, c) == sym for i in range(n)):
#             return True
#         # main diagonal (top-left → bottom-right) = cells where row == col: (0,0),(1,1),(2,2)...
#         # Only relevant if OUR cell is on it, i.e. r == c.
#         if r == c and all(self.board.get(i, i) == sym for i in range(n)):
#             return True
#         # anti-diagonal (top-right → bottom-left) = cells where row+col == n-1: (0,2),(1,1),(2,0)
#         # for n=3. Only relevant if r + c == n-1. The cell (i, n-1-i) walks that diagonal.
#         if r + c == n - 1 and all(self.board.get(i, n - 1 - i) == sym for i in range(n)):
#             return True
#         return False
