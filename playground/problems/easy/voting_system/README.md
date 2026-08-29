# Polling / Voting System 🟢 Easy

**Format:** machine-coding · **Asked as:** a common "model this small app" warm-up · **Time budget:**
40 min · **Patterns:** none forced — clean modeling + invariants (one-vote-per-voter)

> A small, well-scoped modeling problem. The interesting invariants are **one vote per voter per
> poll** and **no voting on a closed poll** — get those right and it's clean.

---

## The prompt

> "Design a polling/voting system. An admin creates a poll with a question and a fixed set of options.
> Users cast a vote for one option. Each user may vote at most once per poll. Show live tallies. A
> closed poll accepts no more votes."

## Clarify before coding

- One vote per voter, and can they change it? *"One vote, immutable for the base; changing is a follow-up."*
- Fixed options at creation, or add later? *"Fixed at creation."*
- Anonymous or identified voters? *"Identified (voter id) so we can enforce one-vote."*
- Results visible during voting? *"Yes, live tallies."*

## Core requirements

1. `create_poll(poll_id, question, options)` — options is a non-empty list.
2. `vote(poll_id, voter_id, option)` — record a vote; reject: unknown poll, invalid option,
   a voter who already voted, or a closed poll (`VotingError`).
3. `results(poll_id)` → `{option: count}` for all options (zeros included).
4. `close_poll(poll_id)` — no further votes accepted.

## Design hints

Nouns → `Poll` (question, options, status, votes), `VotingSystem` (manages polls). Track voters who
have voted per poll in a set for O(1) duplicate detection. No pattern needed — resist the urge; the
signal here is clean invariants and validation, not machinery.

## Follow-ups (escalations)

1. **Change/retract a vote** before the poll closes (adjust tallies).
2. **Multiple-choice** polls (vote for up to k options) — a small rule change; where does it live?
3. **Ranked-choice / weighted** voting — this is where **Strategy** (a tallying strategy) earns its place.
4. **Concurrency:** many voters at once — protect the per-poll tally and voter set.
5. **Scale/audit:** immutable vote log, results as a fold over the log.

## Rubric

- **SDE-1:** correct one-vote-per-voter, option validation, closed-poll rejection, live tallies.
- **SDE-2:** cleanly extends to change-vote / multiple-choice / ranked (Strategy for tallying), and a
  concurrency story for the tally.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
