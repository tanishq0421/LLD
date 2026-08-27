# Meal Builder 🟢 Easy (Builder pattern)

**Format:** machine-coding warm-up · **Asked as:** the standard **Builder** teaching problem
(meal/burger/pizza/HTTP-request builder) · **Time budget:** 30 min · **Patterns:** **Builder**

> Learn **Builder** — for constructing an object that has several optional parts and an invariant
> that must hold when it's finished. Beats a constructor with 8 optional arguments (the
> "telescoping constructor" smell) or a half-initialized mutable object.

---

## The prompt

> "Model building a combo meal. A meal has a name, an optional size, exactly one main item, and any
> number of sides and drinks, each with a price. Assemble a meal step by step, then finalize it — and
> a finalized meal must have at least a main item. Expose the item list and total price."

## Clarify before coding

- Is the main required? *"Yes — a meal isn't valid without a main."*
- Multiple sides/drinks allowed? *"Yes, any number."*
- Should the finished meal be modifiable? *"No — build() produces a finished meal."*

## Core requirements

1. A fluent builder: `add_main`, `add_side`, `add_drink` (each returns the builder for chaining),
   and `set_size`.
2. `build()` returns a finished `Meal` and **validates** at least one main exists (`BuildError` otherwise).
3. `Meal` exposes `name`, `size` (default `"regular"`), `items` (names in insertion order), and
   `total_price`.

## Why Builder (the design point)

The builder accumulates parts and enforces the invariant **once, at `build()`** — the half-built
state never escapes. A telescoping constructor (`Meal(name, main, side1, side2, drink, size, …)`)
or a mutable meal you can leave invalid are the anti-patterns Builder fixes. Note Builder ≠ Factory:
Factory decides *which* object to create; Builder assembles *one complex* object step by step.

## Follow-ups (escalations)

1. **Director:** predefined combos ("Kids Meal", "Value Meal") built via the same builder.
2. **Immutability:** make `Meal` truly immutable; the builder is the only way to construct one.
3. **Validation rules:** max one drink for a kids meal, size affects price — where do these live?
4. Contrast with a data-class + validation function — when is Builder overkill?

## Rubric

- **SDE-1:** fluent chaining, correct total/items, main-required validation.
- **SDE-2:** finished `Meal` is immutable, invariants enforced only at build(), and can add a
  Director for named combos without changing the builder.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
