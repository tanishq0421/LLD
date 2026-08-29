"""
Test contract for the Payment Gateway.

Your `solution.py` must define `PaymentGateway` and a `PaymentError` exception.

Status strings: "AUTHORIZED", "CAPTURED", "PARTIALLY_REFUNDED", "REFUNDED".

    class PaymentGateway:
        def charge(self, idempotency_key: str, amount: int) -> str:
            # Create an AUTHORIZED payment and return its payment_id.
            # IDEMPOTENT: if idempotency_key was used before, return the SAME payment_id and do NOT
            # create a new payment or change the original amount.

        def capture(self, payment_id: str) -> str:
            # AUTHORIZED -> CAPTURED (captured_amount becomes the payment amount). Return new status.
            # Raise PaymentError if not currently AUTHORIZED.

        def refund(self, payment_id: str, amount: int = None) -> str:
            # Refund on a captured payment. `amount=None` refunds the remaining balance.
            # Cumulative refunds must not exceed captured_amount. Return new status:
            #   fully refunded -> "REFUNDED", otherwise -> "PARTIALLY_REFUNDED".
            # Raise PaymentError if the payment isn't captured, amount <= 0, or it would over-refund.

        def status(self, payment_id: str) -> str:
            # Current status. Raise PaymentError if the payment_id is unknown.

        def captured_amount(self, payment_id: str) -> int:
            # The captured amount (0 if not yet captured). Raise PaymentError if unknown.

        def amount_refunded(self, payment_id: str) -> int:
            # Total refunded so far. Raise PaymentError if unknown.

Amounts are positive integers.
"""
