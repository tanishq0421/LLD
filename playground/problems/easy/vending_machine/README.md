# Vending Machine 🟢 Easy (State pattern centerpiece)

**Format:** machine-coding · **Asked by:** Google, Amazon, Microsoft, Apple, Oracle (~20% of
SDE-1 product-company rounds) · **Time budget:** 45 min · **Patterns:** **State** (the whole
point), Strategy (change-making)

---

## The prompt

> "Design a vending machine. It stocks products, each with a code, price, and quantity. A user
> inserts coins to build up a balance, selects a product, and the machine dispenses it and
> returns change. Handle: not enough money, invalid selection, out-of-stock, and cancel/refund.
> Design it so new states or products are easy to add."

## Clarify before coding

- Coin denominations accepted? *"1, 2, 5, 10 units."*
- Select-then-pay, or pay-then-select? *"Either; support inserting coins and selecting in any order, dispense when balance ≥ price."*
- If change can't be made exactly, what happens? *"Assume the machine can always make change for now; flag it as a follow-up."*
- Can the user cancel? *"Yes — refund the full inserted balance."*

## Core requirements

1. `add_product(code, name, price, quantity)` to stock the machine.
2. `insert_coin(denomination)` accumulates balance.
3. `select(code)` chooses a product; rejects invalid code and out-of-stock.
4. `dispense()` requires a selection and `balance ≥ price`; returns `(name, change)`, decrements
   inventory, and resets to the idle state. Rejects if nothing selected or balance insufficient.
5. `refund()` cancels the current interaction and returns the full balance.

## Model it as a State machine (the interviewer wants this)

States: `IDLE` (no selection) → `HAS_SELECTION` (product chosen, collecting money) → dispense →
back to `IDLE`. Out-of-stock and insufficient-balance are guarded transitions. Each state should
decide what `insert_coin` / `select` / `dispense` / `refund` do — the classic **State pattern**:
one class per state, transitions return the next state. Avoid a giant `if self.state == ...` block.

## Follow-ups (escalations)

1. **Exact-change / insufficient-change:** the machine can't always make change — reject the sale
   and refund if it can't. This is a **Strategy** (greedy vs exact denominations available).
2. **Maintenance/admin state:** refill inventory and collect cash; block sales while in it.
3. **Concurrency:** two users interacting with one machine, or concurrent refill vs dispense —
   how do you keep balance and inventory consistent?
4. **Add a new coin type or a new state** without touching existing state classes (OCP).

## Rubric

- **SDE-1:** working flow, all guards (invalid/out-of-stock/insufficient), refund works.
- **SDE-2:** clean State pattern (adding a state = adding a class), change-making as a swappable
  strategy, and a coherent story for concurrency + admin/maintenance.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
