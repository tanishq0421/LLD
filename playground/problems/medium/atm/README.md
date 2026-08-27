# ATM 🟡 Medium (State + Chain of Responsibility)

**Format:** machine-coding + OOD · **Asked by:** Amazon, Adobe, Microsoft, Oracle, banking/fintech
· **Time budget:** 60 min · **Patterns:** **State** (ATM flow), **Chain of Responsibility** (cash
dispenser)

> Two patterns in one problem, which is why it's a favorite. The ATM *flow* is a **State machine**
> (you can't withdraw before authenticating); the *cash dispenser* is a **Chain of Responsibility**
> over note denominations.

---

## The prompt

> "Design an ATM. A user inserts a card, enters a PIN, and — once authenticated — can withdraw cash
> or check balance, then ejects the card. Withdrawals must be dispensed using available notes
> (₹2000/₹500/₹100), rejecting amounts the machine can't make. Model the flow and the dispensing."

## Clarify before coding

- Which denominations? *"2000, 500, 100."*
- Greedy dispensing, or minimum notes? *"Greedy given availability is fine; discuss the exact-change edge case."*
- What happens on wrong PIN? *"Stay in the card-inserted state; reject the operation."*
- Can you withdraw before authenticating? *"No — that must be rejected."*

## Core requirements

1. **State machine:** `IDLE → HAS_CARD → AUTHENTICATED → …` and back to `IDLE` on eject. Operations
   are only valid in the right state (else `ATMError`).
2. `insert_card(card_id)`, `enter_pin(pin)` (correct → AUTHENTICATED; wrong → `ATMError`, stays HAS_CARD).
3. `withdraw(amount)` (AUTHENTICATED only): verify sufficient account balance **and** that the
   machine's notes can make the amount; dispense a `{denom: count}` breakdown; deduct balance and notes.
   Reject (no state change, no deduction) if it can't.
4. `eject_card()` → IDLE.

## Why these patterns

- **State:** each state decides what `withdraw`/`enter_pin` do; illegal transitions are impossible,
  not just guarded by scattered `if`s. Adding an OTP step or a "card blocked" state is an addition.
- **Chain of Responsibility (dispenser):** a handler per denomination (2000 → 500 → 100). Each
  dispenses as many of its note as it can (bounded by availability), then passes the remainder down.
  If a remainder is left at the end, the amount can't be dispensed. Adding a ₹200 note = inserting a
  link, no edits.

## Follow-ups (escalations)

1. **Exact-change failure:** greedy can fail when a valid combination exists (limited notes) → DP.
2. **Concurrency:** shared cash inventory across withdrawals; two users draining the last ₹2000 note.
3. **New states:** OTP/2FA, card-blocked-after-3-wrong-PINs, out-of-service/maintenance.
4. **Deposit, mini-statement, transfer** — more transaction types without bloating the state machine.

## Rubric

- **SDE-1:** correct flow, PIN check, greedy dispensing with availability, all guards.
- **SDE-2:** clean State pattern (new states = additions), dispenser as a real chain, and a story for
  exact-change (DP) + concurrent cash inventory.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
