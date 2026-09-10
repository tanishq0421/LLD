"""
SPLITWISE — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Users; an expense paid by one, split among participants three ways; the system tracks who
   owes whom; balances net across expenses."
    nouns -> User, Expense, Splitwise (the ledger) ; split types = EQUAL/EXACT/PERCENT
    verbs -> add_user, add_expense, get_balance, get_balances

STEP 2 — ENTITIES & RELATIONSHIPS
  Splitwise ◆──── User          COMPOSITION: the ledger owns its user directory (add_user).
  Splitwise o──── Expense       AGGREGATION-ish: an expense is processed into balance deltas and
                                 doesn't need to be kept as an object afterward — we store its
                                 EFFECT (a pairwise balance), not the expense itself. (A passbook
                                 follow-up would keep the Expense objects too.)
  Splitwise ───▶ SplitStrategy  ASSOCIATION: the ledger asks a strategy "how much does each
                                 participant owe?" — it doesn't own the strategy's lifecycle.
  NO inheritance between EQUAL/EXACT/PERCENT and User/Expense — split types differ purely in
  ALGORITHM (how to turn amount+values into a list of shares), which is exactly what Strategy is for.

STEP 3 — PATTERN? (what varies?)
  Strategy (split types). EQUAL / EXACT / PERCENT are three algorithms behind one interface
  `compute(amount, participants, values) -> shares`. `add_expense` picks a strategy by name and
  calls it — adding a fourth type (e.g. SHARES/weighted) is a new class, zero edits to
  `add_expense` (OCP). The alternative — an `if split_type == "EQUAL": ... elif ...` ladder inside
  `add_expense` — is exactly what Strategy avoids: every new type would touch shared code.

STEP 4 — SOLID (+ CONCURRENCY)
  SRP   each *Split class only computes shares; Splitwise only owns users + the balance ledger.
  OCP   new split type = new Strategy class (see STEP 3).
  LSP   every strategy returns a list of floats aligned to `participants`, same shape, so
        `add_expense` never needs to know which one it called.
  CONCURRENCY  two users adding expenses that touch the SAME pair (A,B) at once race on the
        read-modify-write `balances[A][B] += share` — one increment can be lost (classic lost
        update). Fix: a lock per (user-pair) or per user, not one global ledger lock (that would
        serialize unrelated pairs, e.g. (A,B) and (C,D), for no reason).
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (three friends split dinner, balances net) ────────
#   s = Splitwise()
#   s.add_user("u1", "Alice"); s.add_user("u2", "Bob"); s.add_user("u3", "Cara")
#   s.add_expense("u1", 300, ["u1","u2","u3"], "EQUAL")   # each share = 100 -> u2,u3 owe u1 100
#   s.get_balance("u2", "u1")                             # 100.0  (u2 owes u1)
#   s.add_expense("u2", 30, ["u1","u2"], "EQUAL")         # u1 owes u2 15 -> nets against the 100
#   s.get_balance("u2", "u1")                             # 85.0   (100 - 15, netted)
#   s.get_balances("u2")                                  # {"u1": 85.0}
#   # Flow: add_expense -> pick Strategy by split_type -> compute() shares -> for each participant
#   #       (skip payer) apply balances[p][payer] += share ; balances[payer][p] -= share (mirror).
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# from collections import defaultdict


# class SplitError(Exception):
#     pass


# # LOGIC: every strategy exposes the SAME shape: compute(amount, participants, values) -> list of
# # shares, one per participant, IN THE SAME ORDER as `participants`. That uniform return is what
# # lets add_expense stay a one-line dispatch regardless of which strategy ran.

# class EqualSplit:
#     def compute(self, amount, participants, values):
#         n = len(participants)
#         # LOGIC: split evenly and round each share to cents first (money is 2-decimal granular).
#         # Example: 100 / 3 = 33.333... -> round to 33.33 each, but 3*33.33 = 99.99, a cent short.
#         base = round(amount / n, 2)
#         shares = [base] * n
#         # LOGIC: dump the missing/extra cent(s) on the LAST participant so shares always sum to
#         # exactly `amount` (no money lost/created to rounding).
#         leftover = round(amount - base * n, 2)
#         if leftover:
#             shares[-1] = round(shares[-1] + leftover, 2)
#         return shares


# class ExactSplit:
#     def compute(self, amount, participants, values):
#         if values is None or len(values) != len(participants):
#             raise SplitError("EXACT requires one value per participant")
#         # LOGIC: exact shares must account for the whole bill — no silent gap or overcharge.
#         if round(sum(values), 2) != round(amount, 2):
#             raise SplitError("EXACT values must sum to amount")
#         return [round(v, 2) for v in values]


# class PercentSplit:
#     def compute(self, amount, participants, values):
#         if values is None or len(values) != len(participants):
#             raise SplitError("PERCENT requires one value per participant")
#         if round(sum(values), 2) != 100:
#             raise SplitError("PERCENT values must sum to 100")
#         # LOGIC: turn each percentage into a money share. Example: amount=1000, pct=30 -> 300.0.
#         return [round(amount * pct / 100, 2) for pct in values]


# STRATEGIES = {"EQUAL": EqualSplit(), "EXACT": ExactSplit(), "PERCENT": PercentSplit()}


# class Splitwise:
#     def __init__(self):
#         self.users = {}          # user_id -> (name, email, mobile)   membership + profile
#         # LOGIC: balances[a][b] = net amount `a` owes `b`. A defaultdict-of-defaultdict means
#         # reading an unset pair (no shared history) returns 0.0 instead of raising KeyError.
#         self.balances = defaultdict(lambda: defaultdict(float))

#     def add_user(self, user_id, name="", email="", mobile=""):
#         self.users[user_id] = (name, email, mobile)

#     def add_expense(self, paid_by, amount, participants, split_type, values=None):
#         if paid_by not in self.users:
#             raise SplitError(f"unknown payer: {paid_by}")
#         for p in participants:
#             if p not in self.users:
#                 raise SplitError(f"unknown participant: {p}")
#         strategy = STRATEGIES.get(split_type)
#         if strategy is None:
#             raise SplitError(f"unknown split type: {split_type}")
#         shares = strategy.compute(amount, participants, values)   # validates length/sums itself
#         # LOGIC: for every participant OTHER than the payer, they now owe the payer their share.
#         # Mirror the update on both sides so get_balance(a,b) and get_balance(b,a) are always
#         # negatives of each other — that's what "symmetric" balances means.
#         for p, share in zip(participants, shares):
#             if p == paid_by or share == 0:
#                 continue                                   # payer doesn't owe themselves
#             self.balances[p][paid_by] += share              # p owes paid_by more
#             self.balances[paid_by][p] -= share              # paid_by "owes" p less (mirror)

#     def get_balance(self, a, b):
#         # LOGIC: .get(a, {}) avoids the defaultdict's auto-vivification (we don't want a bare
#         # lookup to silently create an empty ledger row for a user who never transacted).
#         return round(self.balances.get(a, {}).get(b, 0.0), 2)

#     def get_balances(self, user_id):
#         row = self.balances.get(user_id, {})
#         # LOGIC: only NON-ZERO balances are shown; netting can bring a pair back to exactly 0
#         # (settled), and float arithmetic can leave a near-zero residue — round before filtering.
#         return {other: round(amt, 2) for other, amt in row.items() if round(amt, 2) != 0}
