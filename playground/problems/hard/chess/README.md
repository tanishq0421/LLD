# Chess 🔴 Hard

**Format:** machine-coding + OOD · **Asked by:** Amazon, Adobe, Meta, Microsoft, Games24x7 (reported
in ~30% of LLD rounds at some) · **Time budget:** 75–90 min · **Patterns:** **Factory** (piece
creation), **polymorphism/Strategy** (per-piece move rules), State (game status)

> The classic "show me your OOD" problem. The winning move is to make each piece responsible for its
> own move legality (polymorphism), so `Game.move` stays tiny. **Scope it down** — nobody implements
> full checkmate in 90 minutes. Get piece movement, path-blocking, captures, and turns right first.

---

## The prompt

> "Design a chess game. Set up the standard board. Support making moves between squares (algebraic
> like `e2`→`e4`): validate the piece belongs to the side to move, that the move is legal for that
> piece type, that the path is clear for sliding pieces, and that you don't capture your own piece.
> Alternate turns. (Check/checkmate/castling can come later.)"

## Clarify before coding (scope hard)

- Full rules or core movement? *"Core movement + captures + turns first. Check/checkmate/castling/
  en passant/promotion are explicit follow-ups — don't start there."*
- Square notation? *"Algebraic: files a–h, ranks 1–8, e.g. `e2`."*
- Do we prevent moving into check in the base? *"No — that's a follow-up; base just enforces per-piece legality."*

## Core requirements

1. Standard starting position; `piece_at(square)` returns codes like `"wP"`, `"bK"`, or `None`.
2. `turn` alternates, White first.
3. `move(from, to)`:
   - the from-square holds a piece of the side to move (else `IllegalMove`);
   - the move is legal for that piece type (pawn/knight/bishop/rook/queen/king rules);
   - for sliding pieces (bishop/rook/queen) the path is clear;
   - the destination isn't occupied by your own piece;
   - captures remove the enemy piece.
4. Illegal moves raise `IllegalMove` and change nothing.

## Why polymorphism + Factory

Each piece type implements its own `is_legal_move(board, from, to)` (or generates its moves).
`Game.move` just asks the piece — no giant `if piece_type == "knight"` switch. A **Factory** builds
the right piece objects when setting up the board. Adding a fairy piece = a new class. This is the
single biggest thing interviewers look for here; avoid deep inheritance beyond the `Piece` base.

## Follow-ups (escalations)

1. **Check detection** (is the king attacked?) and **illegal to move into check**.
2. **Checkmate / stalemate.**
3. **Special moves:** castling, en passant, pawn promotion.
4. **Move history + undo** (Command/Memento), draw by repetition.
5. **Board representation** trade-offs (2D array vs bitboards) for performance.

## Rubric

- **SDE-1:** correct per-piece movement, path-blocking, captures, turn alternation.
- **SDE-2:** clean polymorphic pieces + Factory (new piece = new class), decisively scopes the
  problem, and sketches how check/checkmate/special-moves layer on without a rewrite.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
