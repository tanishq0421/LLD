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

# ─── STEP 5 · HOW IT'S USED (charge → capture → refund, retry-safe) ───────────
#   gw = PaymentGateway()
#   p = gw.charge("idem-abc", 500)     # brand-new AUTHORIZED payment → "PAY1"
#   gw.charge("idem-abc", 500)         # RETRY with the SAME key → returns "PAY1", does NOT charge again
#   gw.capture(p)                      # AUTHORIZED → CAPTURED (captured_amount = 500)
#   gw.refund(p, 200)                  # partial → "PARTIALLY_REFUNDED" (refunded 200)
#   gw.refund(p)                       # amount=None → refund the remaining 300 → "REFUNDED"
#   gw.refund(p, 1)                    # nothing left → PaymentError (state guard)
#   # Flow:  client → gateway.charge (idempotency-key lookup first) → every later call is a GUARDED transition.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import itertools


# class PaymentError(Exception):
#     pass


# class PaymentGateway:
#     def __init__(self):
#         self.payments = {}   # payment_id -> {"amount","status","captured","refunded"}
#         self.keys = {}       # idempotency_key -> payment_id   (the "have I seen this request?" memory)
#         self._seq = itertools.count(1)

#     def charge(self, idempotency_key, amount):
#         # IDEMPOTENCY — the whole trick, in 2 lines: if we've seen this key, return the ORIGINAL
#         # payment id and stop. So a client that retries a timed-out charge gets the same payment,
#         # never a second one. (This is why the key must come from the CLIENT and be stable per attempt.)
#         if idempotency_key in self.keys:
#             return self.keys[idempotency_key]
#         pid = f"PAY{next(self._seq)}"
#         # a fresh payment starts AUTHORIZED (money reserved, not yet taken); nothing captured/refunded.
#         self.payments[pid] = {"amount": amount, "status": "AUTHORIZED",
#                               "captured": 0, "refunded": 0}
#         self.keys[idempotency_key] = pid          # remember key → payment for future retries
#         return pid

#     def _get(self, pid):
#         p = self.payments.get(pid)
#         if p is None:
#             raise PaymentError("unknown payment")
#         return p

#     def capture(self, pid):
#         p = self._get(pid)
#         # STATE GUARD: capture is only legal from AUTHORIZED. This one check makes "capture twice"
#         # and "capture something already refunded" impossible.
#         if p["status"] != "AUTHORIZED":
#             raise PaymentError("can only capture an AUTHORIZED payment")
#         p["status"] = "CAPTURED"
#         p["captured"] = p["amount"]               # the full authorized amount is now actually taken
#         return p["status"]

#     def refund(self, pid, amount=None):
#         p = self._get(pid)
#         # STATE GUARD: you can only refund money that was actually captured. PARTIALLY_REFUNDED is
#         # included so you can refund the rest in more than one step.
#         if p["status"] not in ("CAPTURED", "PARTIALLY_REFUNDED"):
#             raise PaymentError("can only refund a captured payment")
#         remaining = p["captured"] - p["refunded"]  # how much is still refundable right now
#         amount = remaining if amount is None else amount   # None = "refund whatever's left"
#         # never refund ≤ 0, and never MORE than remains (that would refund money you never took).
#         if amount <= 0 or amount > remaining:
#             raise PaymentError("invalid refund amount")
#         p["refunded"] += amount
#         # LOGIC: if we've now refunded everything captured → fully REFUNDED; else PARTIALLY_REFUNDED
#         # (which loops back into this method for the next chunk).
#         p["status"] = "REFUNDED" if p["refunded"] == p["captured"] else "PARTIALLY_REFUNDED"
#         return p["status"]

#     def status(self, pid):
#         return self._get(pid)["status"]

#     def captured_amount(self, pid):
#         return self._get(pid)["captured"]

#     def amount_refunded(self, pid):
#         return self._get(pid)["refunded"]
