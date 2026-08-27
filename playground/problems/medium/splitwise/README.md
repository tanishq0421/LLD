# Splitwise (Expense Sharing) 🟡 Medium

**Format:** machine-coding (very common) · **Asked by:** Swiggy, Amazon, Razorpay, most Indian
fintech/product cos · **Time budget:** 60–90 min · **Patterns:** **Strategy** (split types)

> Swiggy is reported to give this almost verbatim as its machine-coding round. The spec is handed
> fairly concretely (unusual — most of the 90 minutes is meant for *code quality*, not requirement
> archaeology). The interesting design decision is making split types **open for extension**.

---

## The prompt (near-verbatim, as handed out)

> "Create an expense-sharing application. Users can add an expense paid by one person and split it
> among a set of people. Each user has an id, name, email, and mobile. Support three split types:
> **EQUAL** (split equally), **EXACT** (each person's exact share is given), and **PERCENT** (each
> person's percentage is given — percentages must sum to 100). The system tracks who owes whom.
> Support showing all balances, or balances for a single user. Show only non-zero balances."

Stretch goals often mentioned: expense notes/metadata, a per-user transaction history
("passbook"), and **debt simplification** (minimize the number of transactions to settle up).

## Clarify before coding

- Is the payer always part of the split group? *"They may or may not be — handle both."*
- EXACT/PERCENT values align to the participant list order? *"Yes."*
- How to handle amounts that don't divide evenly (e.g. 100/3)? *"Round to 2 decimals; ask about the leftover cent."*
- Do balances **net out** across multiple expenses? *"Yes — if A owes B 100 and B owes A 30, net is A owes B 70."*

## Core requirements

1. `add_user(user_id, name, email, mobile)`.
2. `add_expense(paid_by, amount, participants, split_type, values)`:
   - `EQUAL`: split equally among participants (`values` ignored).
   - `EXACT`: `values` are exact shares; must sum to `amount`.
   - `PERCENT`: `values` are percentages; must sum to 100.
   - Validate: users exist, `values` length matches participants, sums are correct → else `SplitError`.
3. `get_balance(a, b)` → net amount **a owes b** (negative means b owes a, 0 = settled).
4. `get_balances(user_id)` → dict of non-zero balances for that user.
5. Balances **net** across expenses.

## Make split types a Strategy (the key design signal)

`EQUAL / EXACT / PERCENT` are three algorithms behind one interface `split(amount, participants,
values) -> shares`. Adding a new split type (e.g. `SHARES`/weighted) = a new Strategy class, no edits
to `add_expense` (**OCP**). Contrast with an `if split_type == ...` ladder you'd edit each time.

## Follow-ups (escalations)

1. **Debt simplification:** minimize transactions to settle all balances (net everyone, then match
   the biggest creditor with the biggest debtor greedily). A classic, genuinely harder follow-up.
2. **New split type** `WEIGHTED` (by shares) — prove your Strategy makes this a pure addition.
3. **Transaction history / passbook** per user.
4. **Concurrency:** many users adding expenses at once — what state needs protecting?
5. **Uneven division:** 100 split 3 ways = 33.33/33.33/33.34 — who absorbs the extra cent?

## Rubric

- **SDE-1:** correct balances for all three split types, validation, netting across expenses.
- **SDE-2:** split types cleanly as Strategy, a working debt-simplification approach, and a story
  for rounding + concurrency.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
