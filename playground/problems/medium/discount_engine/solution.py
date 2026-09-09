"""
DISCOUNT ENGINE — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

WHY THIS ONE FOR BLINKIT: quick-commerce runs on offers. A growth team adds promo types weekly,
so the design must let a NEW rule drop in without editing the engine — that's the whole point,
and it's a clean Strategy + Chain-of-Responsibility showcase.

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES
  "Cart of items; apply a sequence of discount rules to the total; never below 0."
    nouns -> Cart, DiscountEngine, Rule ; verbs -> add_item, add_rule, total

STEP 2 — ENTITIES & RELATIONSHIPS
  Cart ◆──── items            COMPOSITION: items live inside the cart.
  Engine o──── Rule           the engine holds an ORDERED list of rules; a Rule is a Strategy —
                              here a callable rule(cart, running_total) -> new_total (could be a
                              class with __call__ instead; same shape).
  Engine ───▶ Cart            the total() reads the cart's subtotal, then folds rules over it.

STEP 3 — PATTERNS (two, both justified)
  • STRATEGY — each discount is an interchangeable unit of the SAME shape (percentage, flat,
    threshold, BOGO...). New promo = new strategy, engine untouched (OCP).
  • CHAIN OF RESPONSIBILITY — the engine passes the RUNNING total through each rule in order;
    a rule may change it or pass it through (e.g. threshold no-ops if subtotal too low).
  Decisions to say out loud:
    - stacking ORDER matters (10%-then-₹5-off ≠ ₹5-off-then-10%) → apply in configured order.
    - percentage applies to the RUNNING total; threshold checks the ORIGINAL subtotal.
    - floor at 0 so a big flat discount can't make the total negative.

STEP 4 — SOLID + FOLLOW-UPS
  OCP is the star: a custom rule is just another callable you add_rule().
  FOLLOW-UPS: exclusive ("best single wins" → max instead of chain), item-level/BOGO (needs the
  cart, not just the total), caps ("max ₹100 off"), a savings breakdown for audit.
────────────────────────────────────────────────────────────────────────────
"""

# ===== SOLUTION (study, then write your own active version) =====


# class Cart:
#     def __init__(self):
#         self.items = []                    # list of (name, price, qty)

#     def add_item(self, name, price, qty=1):
#         self.items.append((name, price, qty))

#     def subtotal(self):
#         return sum(price * qty for _, price, qty in self.items)


# class DiscountEngine:
#     def __init__(self):
#         self.rules = []                    # ORDERED list of rule callables (the chain)

#     def add_rule(self, rule):
#         # a rule is any callable rule(cart, running_total) -> new_total. Keeping it a callable
#         # means built-ins AND user lambdas AND rule-classes all just work (Strategy).
#         self.rules.append(rule)

#     def total(self, cart):
#         t = cart.subtotal()
#         for rule in self.rules:            # CHAIN: thread the running total through each rule
#             t = rule(cart, t)
#         return round(max(0, t), 2)         # floor at 0, round money to 2dp

#     # --- built-in rule BUILDERS: each RETURNS a strategy callable (a closure over its config) ---
#     @staticmethod
#     def percentage(pct):
#         return lambda cart, t: t * (1 - pct / 100)

#     @staticmethod
#     def flat(amount):
#         return lambda cart, t: max(0, t - amount)

#     @staticmethod
#     def threshold(min_subtotal, amount):
#         # NOTE: gate on the ORIGINAL subtotal (cart.subtotal()), not the discounted running total.
#         return lambda cart, t: max(0, t - amount) if cart.subtotal() >= min_subtotal else t
