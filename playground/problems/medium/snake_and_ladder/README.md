# Snake & Ladder 🟡 Medium

**Format:** machine-coding · **Asked by:** Flipkart/Swiggy-style machine-coding rounds (board-game
family) · **Time budget:** 45–60 min · **Patterns:** Factory (board entities), Strategy (dice /
win rule)

> A "can you orchestrate a stateful game cleanly" problem. The trap is hard-coding rules and
> randomness so it's untestable — good candidates **inject the dice** so runs are reproducible.

---

## The prompt

> "Design the game Snake & Ladder. A board has numbered cells (say 1–100). Players take turns
> rolling a die and advancing. Landing on a ladder's bottom moves you up to its top; landing on a
> snake's head moves you down to its tail. First player to reach the final cell wins. You must land
> exactly on the final cell — an overshoot means you don't move that turn."

## Clarify before coding

- Board size fixed at 100? *"Configurable."*
- Exact landing to win, or overshoot-and-bounce? *"Exact landing; overshoot = stay put."*
- Does rolling a 6 grant another turn? *"No for the base version — treat it as a follow-up."*
- Can a jump chain (ladder top is another ladder bottom)? *"No — apply at most one jump per move."*
- Multiple players? *"Yes, 2+."*

## Core requirements

1. Configurable board size, snakes (`head → tail`, head > tail), ladders (`bottom → top`, bottom < top).
2. Players move in turn order; positions start off-board at 0.
3. A roll advances the player; apply one snake/ladder jump if the landing cell has one.
4. Overshooting the final cell = no move.
5. Reaching the final cell exactly = win; game ends.
6. **Injectable dice** so games are reproducible (default random 1–6).

## Design hints

Nouns → `Board`, `Snake`/`Ladder` (or a `Jump` with from/to), `Player`, `Dice`, `Game`. A `Board`
that stores a `jumps` map (cell → destination) built from snakes+ladders keeps `Game.play_turn`
tiny. Keep randomness behind a `Dice` object you can replace with a scripted one (this is the
**Strategy**/dependency-injection move that makes it testable).

## Follow-ups (escalations)

1. **Roll-a-6 grants another turn** (and three 6s in a row = forfeit turn).
2. **Multiple dice** / different win rule (bounce-back on overshoot) — swap the Strategy.
3. **Validate the board** at construction (no snake/ladder starting on the same cell, none on cell
   1 or the last cell).
4. **Chained jumps** (ladder → ladder).
5. **N players, track ranking** as they finish, not just first winner.

## Rubric

- **SDE-1:** correct movement, jumps, overshoot, win detection; dice injectable.
- **SDE-2:** board validation, clean separation (Board/Dice/Game), and rule variants (extra turn,
  win rule) added without rewriting the turn loop.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
