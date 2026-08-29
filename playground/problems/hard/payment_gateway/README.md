# Payment Gateway / Transaction Processor 🔴 Hard

**Format:** machine-coding + OOD · **Asked by:** Stripe, PayPal, Square, Razorpay, Amazon · **Time
budget:** 75 min · **Patterns:** **State** (payment lifecycle), idempotency keys, Strategy (providers)

> A fintech favorite. Two things make it hard and make it *senior*: a strict **state machine**
> (you can't refund before capture) and **idempotency** — the same charge request must never double-
> charge, even if the client retries. Idempotency is the concept interviewers are really probing.

---

## The prompt

> "Design the core of a payment gateway. A charge goes through a lifecycle: authorized → captured →
> refunded (fully or partially). Illegal transitions must be rejected. Crucially, a charge carries an
> **idempotency key**: if the same key is retried (network timeout, double-click), it must return the
> original payment and **not** charge again. Support partial refunds up to the captured amount."

## Clarify before coding

- Lifecycle states? *"AUTHORIZED → CAPTURED → PARTIALLY_REFUNDED → REFUNDED (illegal jumps rejected)."*
- What does the idempotency key guarantee? *"Same key ⇒ same payment, exactly once — retries are safe."*
- Partial refunds? *"Yes, cumulative up to the captured amount."*
- Refund before capture? *"Rejected."*

## Core requirements

1. `charge(idempotency_key, amount)` → `payment_id`, creating an `AUTHORIZED` payment. **Idempotent:**
   the same key returns the *same* payment_id and does **not** create a second payment or re-charge.
2. `capture(payment_id)` — `AUTHORIZED → CAPTURED`; illegal otherwise (`PaymentError`).
3. `refund(payment_id, amount=None)` — only on captured payments; cumulative refunds ≤ captured
   amount; `None` means refund the remaining balance. Full → `REFUNDED`, partial → `PARTIALLY_REFUNDED`.
4. Queries: `status`, `captured_amount`, `amount_refunded`.

## Why State + idempotency

- **State machine:** each transition is guarded; you cannot refund an authorized-but-not-captured
  payment or capture twice. Model states explicitly so illegal transitions are impossible, not just
  discouraged.
- **Idempotency key:** the gateway remembers `key → payment_id`. A retry with the same key short-
  circuits to the existing payment. This is *the* mechanism that makes money movement safe under
  at-least-once network delivery — be ready to explain it clearly.

## Follow-ups (escalations)

1. **Provider abstraction:** route to Stripe/Razorpay/PayPal via an **Adapter/Strategy**; failover.
2. **Async webhooks / retries** for capture confirmation; reconciliation.
3. **Idempotency-key expiry** and conflicts (same key, *different* amount → reject as a conflict).
4. **Fraud checks, 3DS/OTP** as an extra state; **void** an authorization before capture.
5. **Concurrency:** two retries with the same key racing — must still create exactly one payment.

## Rubric

- **SDE-1:** correct lifecycle transitions, partial/full refunds, basic idempotency (same key ⇒ same id).
- **SDE-2:** explains idempotency under at-least-once delivery + the concurrent-retry race, models the
  state machine cleanly (illegal transitions impossible), and sketches provider Adapter + async webhooks.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
