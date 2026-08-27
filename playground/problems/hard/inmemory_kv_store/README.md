# In-memory Key-Value Store with Transactions 🔴 Hard

**Format:** machine-coding · **Asked by:** Razorpay ("in-memory SQL-like DB"), Amazon, Google,
ThoughtWorks-style rounds · **Time budget:** 60–90 min · **Patterns:** Command/Memento-lite
(layered undo), Composite-ish (nested scopes)

> A deceptively deep problem. `get/set/delete` is a warm-up; **nested transactions with
> commit/rollback** are where candidates tangle themselves. The clean solution is a **stack of
> overlay layers** — get to it and this becomes elegant instead of a maze of if-statements.

---

## The prompt

> "Implement an in-memory key-value store that supports transactions. Besides `get`, `set`, and
> `delete`, support `begin`, `commit`, and `rollback`. Transactions can be **nested**. Changes made
> inside a transaction are only visible within it until committed; `rollback` discards them."

## Clarify before coding (nail the semantics — they're the whole problem)

- Does `commit` close all open transactions, or merge just the innermost into its parent? *"Merge
  the innermost into its parent (or the base store if it's the outermost). Nesting-friendly."*
- What does `get` return for a missing/deleted key? *"None."*
- `commit`/`rollback` with no open transaction? *"Raise an error."*
- Are `None` values stored? *"No — values are non-None; treat None as absent."*

## Exact semantics (agreed)

- `begin()` — open a new (possibly nested) transaction layer.
- `set(k, v)` / `delete(k)` — apply to the innermost open layer (or the base store if none open).
- `get(k)` — the effective value looking from the innermost layer down to the base; `None` if unset
  or deleted in the nearest layer that mentions it.
- `rollback()` — discard the innermost layer's changes. Error (`NoTransaction`) if none open.
- `commit()` — apply the innermost layer's changes onto its parent (or base) and close that layer.
  Error (`NoTransaction`) if none open.
- `count(value)` — how many keys currently map to `value` (a classic add-on).

## Design hint — the overlay stack

Keep a `base` dict and a stack of **overlay** dicts. In an overlay, a key can map to a real value
or to a `DELETED` sentinel. `get` walks the stack top-down; `set`/`delete` write to the top overlay;
`commit` folds the top overlay into the one beneath; `rollback` pops it. This makes every operation
a few lines and nesting falls out for free — a small example of layered/Memento-style state.

## Follow-ups (escalations)

1. **`count(value)`** efficiently (maintain a value→count index per layer instead of scanning).
2. **Isolation under concurrency:** two threads each with their own transaction — what's shared,
   what's per-transaction? (Real DBs: MVCC / snapshot isolation.)
3. **TTL / expiry** on keys.
4. **`commit` that closes ALL open transactions** as an alternate semantic — how does your design flex?
5. **Persistence / write-ahead log** so state survives restart.

## Rubric

- **SDE-1:** correct get/set/delete, single-level begin/commit/rollback, error on no transaction.
- **SDE-2:** clean overlay-stack handling arbitrary **nesting**, correct `commit`-merges-one-level
  semantics, efficient `count`, and a coherent concurrency-isolation story.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
