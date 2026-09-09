"""
PAYMENT GATEWAY — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

WHY THIS ONE FOR myKaarma: they take dealership payments, and IDEMPOTENCY (a retried charge must
never double-charge) is the concept payment interviewers probe. Be able to explain it in one
sentence: "the key makes a repeated request return the original result instead of acting again."

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES
  "A charge goes authorized -> captured -> refunded (full/partial); illegal jumps rejected;
   a retried charge (same idempotency key) must not charge twice."
    nouns -> PaymentGateway, Payment ; verbs -> charge, capture, refund, status

STEP 2 — ENTITIES & RELATIONSHIPS
  Gateway ◆──── Payment       COMPOSITION: the gateway owns its payment records.
  Gateway ──── key index      a map idempotency_key -> payment_id (the exactly-once memory).
  A Payment carries: amount, status, captured_amount, refunded so far.

STEP 3 — TWO IDEAS (this is what makes it "senior")
  (a) STATE MACHINE — a Payment is in exactly one status and only legal transitions are allowed:
        AUTHORIZED --capture--> CAPTURED --refund(partial)--> PARTIALLY_REFUNDED --refund--> REFUNDED
      You CANNOT refund an AUTHORIZED (not-yet-captured) payment, or capture twice. Model status
      explicitly and GUARD every transition → illegal states become impossible, not just unlikely.
      (Full State pattern with a class per state is overkill here; an explicit status field +
       guards is the right amount. Say that — knowing when NOT to use the pattern scores.)
  (b) IDEMPOTENCY KEY — the safety mechanism for money under at-least-once networks. On charge:
        if key already seen -> return the SAME payment_id, do NOT create/charge again.
      This is why a client can safely retry a timed-out charge. One dict lookup; huge correctness.

STEP 4 — SOLID + FOLLOW-UPS + CONCURRENCY
  SRP  each method is one transition; queries are pure reads.
  FOLLOW-UPS: provider Adapter/Strategy (Stripe/Razorpay) + failover; async webhooks; key
  EXPIRY and conflict (same key, different amount -> reject); void-before-capture; 3DS/OTP state.
  CONCURRENCY: two retries with the same key racing must still create exactly ONE payment → lock
  (or upsert on the key) around the "seen this key?" check.
────────────────────────────────────────────────────────────────────────────
"""

# ===== SOLUTION (study, then write your own active version) =====

# import itertools


# class PaymentError(Exception):
#     pass


# class PaymentGateway:
#     def __init__(self):
#         self.payments = {}   # payment_id -> {"amount","status","captured","refunded"}
#         self.keys = {}       # idempotency_key -> payment_id   (the exactly-once memory)
#         self._seq = itertools.count(1)

#     def charge(self, idempotency_key, amount):
#         # IDEMPOTENCY: seen this key before? return the original payment, don't charge again.
#         if idempotency_key in self.keys:
#             return self.keys[idempotency_key]
#         pid = f"PAY{next(self._seq)}"
#         self.payments[pid] = {"amount": amount, "status": "AUTHORIZED",
#                               "captured": 0, "refunded": 0}
#         self.keys[idempotency_key] = pid
#         return pid

#     def _get(self, pid):
#         p = self.payments.get(pid)
#         if p is None:
#             raise PaymentError("unknown payment")
#         return p

#     def capture(self, pid):
#         p = self._get(pid)
#         # STATE GUARD: capture is only legal from AUTHORIZED.
#         if p["status"] != "AUTHORIZED":
#             raise PaymentError("can only capture an AUTHORIZED payment")
#         p["status"] = "CAPTURED"
#         p["captured"] = p["amount"]
#         return p["status"]

#     def refund(self, pid, amount=None):
#         p = self._get(pid)
#         # STATE GUARD: refund only after capture (CAPTURED or already PARTIALLY_REFUNDED).
#         if p["status"] not in ("CAPTURED", "PARTIALLY_REFUNDED"):
#             raise PaymentError("can only refund a captured payment")
#         remaining = p["captured"] - p["refunded"]
#         amt = remaining if amount is None else amount   # None = refund the remaining balance
#         if amt <= 0 or amt > remaining:                 # never over-refund
#             raise PaymentError("invalid refund amount")
#         p["refunded"] += amt
#         # transition depends on whether everything captured is now refunded
#         p["status"] = "REFUNDED" if p["refunded"] == p["captured"] else "PARTIALLY_REFUNDED"
#         return p["status"]

#     def status(self, pid):
#         return self._get(pid)["status"]

#     def captured_amount(self, pid):
#         return self._get(pid)["captured"]

#     def amount_refunded(self, pid):
#         return self._get(pid)["refunded"]
