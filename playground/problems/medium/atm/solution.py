"""
ATM — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Insert a card, authenticate with a PIN, check balance, withdraw cash in notes, eject."
    nouns -> ATM, account (card_id/pin/balance), cash tray (denomination -> count)
    verbs -> insert_card, enter_pin, balance, withdraw, eject_card
  A card is just a key into `accounts` — pin/balance are DATA, so an account is a dict entry,
  not a class hierarchy (no "SavingsCard vs CreditCard" behavioural difference here).

STEP 2 — ENTITIES & RELATIONSHIPS
  ATM ◆──── cash tray          COMPOSITION: the note inventory lives and dies with the machine.
  ATM o──── accounts           AGGREGATION/DI: the bank owns the account store; it's PASSED IN
                                (same idea as parking lot's injected clock) so tests control it.
  ATM ───▶ current card_id     ASSOCIATION: "which account is in the slot right now" — one
                                mutable reference, cleared on eject.
  NO inheritance for state names — IDLE/HAS_CARD/AUTHENTICATED is a closed 3-value set, tracked
  as a string field with guard clauses, not a subclass per state.

STEP 3 — PATTERN? (what varies?)
  STATE: every public method's behaviour depends entirely on "which of the 3 states am I in?" —
  each one opens with a state guard. A textbook State pattern would give IDLE/HAS_CARD/
  AUTHENTICATED their own classes, each implementing insert_card/enter_pin/withdraw/... with
  the illegal ones raising. With only 3 states and ~4 methods, that's a lot of ceremony for the
  same transitions a single string + guard clauses already express — so we keep the string, but
  name the seam: "if this grew (PIN_RETRY, CARD_BLOCKED, MENU...) I'd promote it to real State
  classes so each state's file only shows what's legal there."
  CHAIN OF RESPONSIBILITY: the cash dispenser. Walk denominations LARGEST first; each one takes
  as many notes as it can (bounded by what's left to pay AND what's in the tray) and hands the
  REMAINDER to the next-smaller denomination — the classic CoR shape ("try to handle it, pass
  the rest down the chain"), written here as one loop because every link does the identical step.

STEP 4 — SOLID (+ concurrency note)
  SRP   denomination math is one helper (_compose); state transitions are separate guard clauses
        in each method — nobody mixes "am I allowed" with "how much cash is that."
  OCP   a new state (CARD_BLOCKED) or a new dispensing rule (fewest notes, prefer small bills)
        plugs in without touching the other methods.
  CONCURRENCY  a shared backend serving many ATMs must check-balance + check-notes + deduct as
        ONE atomic step (lock per account, or per account+tray) — otherwise two withdrawals
        racing on the same account both read "sufficient funds" and double-spend.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (insert, auth, withdraw, eject) ───────────────────
#   a = ATM(cash={2000: 5, 500: 5, 100: 5}, accounts={"C1": {"pin": "1234", "balance": 10000}})
#   a.state                                    # "IDLE"
#   a.insert_card("C1")                        # known card, IDLE -> HAS_CARD
#   a.enter_pin("1234")                        # matches -> HAS_CARD -> AUTHENTICATED
#   a.balance()                                # 10000
#   out = a.withdraw(2600)                     # greedy chain: 1x2000, 1x500, 1x100 -> exact
#   out                                        # {2000: 1, 500: 1, 100: 1}
#   a.balance()                                # 7400  (deducted only on success)
#   a.eject_card()                             # -> IDLE, card slot cleared
#   # Flow: insert_card/enter_pin walk the state string forward; withdraw computes the whole
#   # dispense plan FIRST (_compose), and only mutates cash/balance if that plan exactly pays
#   # the amount — a failed dispense must leave everything untouched.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# class ATMError(Exception):
#     pass


# class ATM:
#     def __init__(self, cash, accounts):
#         # LOGIC: copy the cash dict so mutating our tray never mutates the caller's original dict
#         # (defensive copy — same spirit as not aliasing mutable args you were handed).
#         self.cash = dict(cash)
#         self.accounts = accounts          # DI: bank's account store, referenced not owned
#         self._state = "IDLE"              # one of IDLE / HAS_CARD / AUTHENTICATED
#         self._card = None                 # card_id currently in the slot, or None

#     @property
#     def state(self):
#         return self._state

#     def insert_card(self, card_id):
#         # LOGIC: guard clause — this method is only legal from IDLE. e.g. inserting a 2nd card
#         # while one is already in the slot must fail, not silently swap it.
#         if self._state != "IDLE":
#             raise ATMError("a card is already inserted")
#         if card_id not in self.accounts:
#             raise ATMError("unknown card")
#         self._card = card_id
#         self._state = "HAS_CARD"

#     def enter_pin(self, pin):
#         if self._state != "HAS_CARD":
#             raise ATMError("insert a card first")
#         if self.accounts[self._card]["pin"] != pin:
#             # LOGIC: wrong PIN does NOT eject the card — contract says stay HAS_CARD so the
#             # customer gets another try (a real ATM would count attempts; out of scope here).
#             raise ATMError("wrong pin")
#         self._state = "AUTHENTICATED"

#     def balance(self):
#         if self._state != "AUTHENTICATED":
#             raise ATMError("not authenticated")
#         return self.accounts[self._card]["balance"]

#     def withdraw(self, amount):
#         if self._state != "AUTHENTICATED":
#             raise ATMError("not authenticated")
#         if amount > self.accounts[self._card]["balance"]:
#             raise ATMError("insufficient funds")
#         # LOGIC: compute the FULL dispense plan before touching any state. If the tray can't
#         # make exact change (e.g. 250 from only 2000/500/100 notes), _compose returns None and
#         # we raise WITHOUT having deducted anything — "on any failure, change nothing."
#         dispensed = self._compose(amount)
#         if dispensed is None:
#             raise ATMError("cannot dispense that amount with available notes")
#         for denom, count in dispensed.items():
#             self.cash[denom] -= count
#         self.accounts[self._card]["balance"] -= amount
#         return dispensed

#     def _compose(self, amount):
#         # CHAIN OF RESPONSIBILITY, as a loop: walk denominations biggest -> smallest. Each one
#         # "handles" floor(remaining / denom) notes, capped by how many are actually in the tray,
#         # then passes what's LEFT to the next (smaller) denomination.
#         # Example: amount=2600, notes {2000:5,500:5,100:5}
#         #   2000: want 2600//2000=1, have 5 -> take 1, remaining = 2600-2000 = 600
#         #   500:  want  600//500 =1, have 5 -> take 1, remaining =  600- 500 = 100
#         #   100:  want  100//100 =1, have 5 -> take 1, remaining =  100- 100 =   0  -> done
#         remaining = amount
#         dispensed = {}
#         for denom in sorted(self.cash, reverse=True):   # descending: 2000, 500, 100, ...
#             if remaining <= 0:
#                 break
#             take = min(remaining // denom, self.cash[denom])
#             if take:
#                 dispensed[denom] = take
#                 remaining -= take * denom
#         # LOGIC: if we couldn't whittle `remaining` down to exactly 0 (not enough notes of the
#         # right sizes — e.g. 250 needs a 50, which doesn't exist), the amount is undispensable.
#         return dispensed if remaining == 0 else None

#     def eject_card(self):
#         # LOGIC: legal from ANY state (contract: "-> IDLE from any state"), so no guard here —
#         # eject is the universal escape hatch, unlike the other transitions.
#         self._state = "IDLE"
#         self._card = None
