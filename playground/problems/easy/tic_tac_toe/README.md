# Tic-Tac-Toe 🟢 Easy

**Format:** machine-coding / OOD warm-up · **Asked by:** widely, as a junior/first-round filter
· **Time budget:** 30–40 min · **Patterns:** State-lite, (Strategy if you generalize win rules)

---

## The prompt (as an interviewer gives it)

> "Design and implement a two-player Tic-Tac-Toe game. Two players take turns placing their
> marks on a 3×3 grid; the first to get three in a row — horizontally, vertically, or
> diagonally — wins. If the board fills with no winner, it's a draw. Model it cleanly and make
> it runnable."

This one is usually given fairly concretely — it's a warm-up to check you can model a small
domain cleanly. The signal is *code quality*, not cleverness.

## Clarify before coding (ask these; typical answers in italics)

- Board size fixed at 3×3, or generalize to N×N? *"Start with 3×3, but design so N is easy."*
- Two human players only, or AI opponent? *"Two players, no AI."*
- Who starts? *"X (player 0) starts."*
- Should the engine reject illegal moves, or trust the caller? *"Reject them explicitly."*

## Core requirements (must-have to pass)

1. Alternating turns between two symbols (`X`, `O`), `X` starts.
2. Placing a mark on an empty in-bounds cell.
3. After each move, report status: `IN_PROGRESS`, `WIN`, or `DRAW`.
4. Reject illegal moves (occupied cell, out of bounds, or moving after the game is over).
5. Expose who won.

## Follow-ups (escalations the interviewer adds live)

1. **Generalize to N×N** with a win condition of N in a row. *(Design for this from the start.)*
2. **Efficiency:** don't re-scan the whole board each move — check only the affected row/column/
   diagonals, O(N) instead of O(N²). *(An SDE-2 signal.)*
3. **Undo the last move.** *(Command / Memento territory — how does your model support it?)*
4. **Generalize win rules** (e.g. Connect-Four gravity, K-in-a-row on an M×N board). Where does
   Strategy fit?

## Design hints (don't over-build)

Nouns → `Board`, `Player`, `Game`(controller), `Symbol`. Keep `Board` responsible only for cells
and placement; keep turn/win/draw logic in `Game`. You do **not** need inheritance here.

## Rubric

- **SDE-1:** correct 3×3 game, illegal moves rejected, clean separation of Board vs Game.
- **SDE-2:** N×N generalized cleanly, O(N) incremental win-check, and a clear answer to undo +
  generalized win-rules without rewriting the core.

## Your task

Write `solution.py` in this folder exposing the interface in [`contract.py`](contract.py), then:

```bash
python3 -m unittest test_solution.py -v
```
