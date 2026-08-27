"""
Test contract for Chess (core movement).

Your `solution.py` must define `ChessGame` and an `IllegalMove` exception.

Squares are algebraic strings: file a-h + rank 1-8, e.g. "e2". Piece codes are 2 chars:
color ("w"/"b") + type ("P","N","B","R","Q","K"), e.g. "wP", "bK".

    class ChessGame:
        def __init__(self):
            # Standard starting position, White to move.

        @property
        def turn(self) -> str:
            # "white" or "black".

        def piece_at(self, square: str):
            # Piece code (e.g. "wP") at that square, or None if empty.

        def move(self, frm: str, to: str) -> None:
            # Make a move. Validate:
            #   - `frm` holds a piece of the side to move (else IllegalMove);
            #   - the move is legal for that piece type;
            #   - sliding pieces (B/R/Q) have a clear path;
            #   - `to` is not occupied by a same-color piece;
            #   - a capture removes the enemy piece.
            # On success, alternate the turn. On any violation raise IllegalMove and change nothing.

Base scope is per-piece movement legality only — NO check/checkmate/castling/en-passant/promotion
(those are follow-ups). Pawns: 1 forward (or 2 from the start rank) to an empty square; capture one
square diagonally forward onto an enemy piece.
"""
