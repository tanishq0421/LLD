"""
Test contract for the ATM (State + Chain of Responsibility).

Your `solution.py` must define `ATM` and an `ATMError` exception.

    class ATM:
        def __init__(self, cash: dict, accounts: dict):
            # cash    : {denomination: count} available notes, e.g. {2000: 5, 500: 5, 100: 5}.
            # accounts: {card_id: {"pin": str, "balance": number}}.

        @property
        def state(self) -> str:
            # "IDLE" | "HAS_CARD" | "AUTHENTICATED".

        def insert_card(self, card_id: str) -> None:
            # IDLE -> HAS_CARD. Raise ATMError if not IDLE or card unknown.

        def enter_pin(self, pin: str) -> None:
            # HAS_CARD -> AUTHENTICATED if pin matches; else raise ATMError (stay HAS_CARD).

        def balance(self) -> float:
            # AUTHENTICATED only; the current account balance. Raise ATMError otherwise.

        def withdraw(self, amount: int) -> dict:
            # AUTHENTICATED only. Validate amount <= balance AND that available notes can make it.
            # On success: return {denom: count} dispensed, deduct balance and notes. Stay AUTHENTICATED.
            # On any failure (wrong state, insufficient funds, cannot dispense): raise ATMError and
            # change NOTHING (no balance/notes deduction).

        def eject_card(self) -> None:
            # -> IDLE from any state.

Dispensing is greedy by descending denomination, bounded by availability.
"""
