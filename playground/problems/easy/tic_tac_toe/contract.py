"""
Test contract for Tic-Tac-Toe.

This is the ONLY constraint on your design — the public surface the tests call. Everything
behind it (classes, how you store the board, how you check wins) is yours to design.

Your `solution.py` must define a `Game` class and an `InvalidMove` exception with this behavior:

    class Game:
        def __init__(self, size: int = 3):
            # Square board of side `size` (>= 3). X (player 0) moves first.

        def move(self, row: int, col: int) -> str:
            # Place the current player's mark at (row, col), 0-indexed.
            # Return the resulting status string: "IN_PROGRESS", "WIN", or "DRAW".
            # Raise InvalidMove if the cell is occupied, out of bounds, or the game is over.
            # Turns alternate automatically; the caller does not pass a player.

        @property
        def current_symbol(self) -> str:
            # "X" or "O" — whose turn it is NOW (before their move).

        @property
        def winner(self):
            # "X", "O", or None if no one has won (yet / draw).

        @property
        def status(self) -> str:
            # "IN_PROGRESS" | "WIN" | "DRAW" — same value the last move() returned.

Status string constants the tests compare against:
    IN_PROGRESS = "IN_PROGRESS"
    WIN         = "WIN"
    DRAW        = "DRAW"

Symbols: "X" for player 0 (moves first), "O" for player 1.
"""

IN_PROGRESS = "IN_PROGRESS"
WIN = "WIN"
DRAW = "DRAW"
