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

# ─── STEP 5 · HOW IT'S USED (build a cart, stack rules) ───────────────────────
#   cart = Cart(); cart.add_item("A", 100, 1); cart.add_item("B", 50, 2)   # subtotal = 200
#   eng = DiscountEngine()
#   eng.add_rule(DiscountEngine.threshold(150, 20))   # subtotal ≥ 150 → −20
#   eng.add_rule(DiscountEngine.percentage(10))       # THEN 10% off the running total
#   eng.total(cart)      # 200 →(threshold)→ 180 →(10%)→ 162.0     (ORDER matters!)
#   # swap the two add_rule lines → 200 →(10%)→ 180 →(−20)→ 160.0  (different result)
#   # Flow:  checkout → Engine.total → cart.subtotal() → fold each rule(cart, running) → floor at 0, round.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====


# class Cart:
#     def __init__(self):
#         self.items = []                    # list of (name, price, qty)

#     def add_item(self, name, price, qty=1):
#         self.items.append((name, price, qty))

#     def subtotal(self):
#         # LOGIC: sum price*qty over every item. The `_` throws away the name we don't need here.
#         return sum(price * qty for _, price, qty in self.items)


# class DiscountEngine:
#     def __init__(self):
#         self.rules = []                    # ORDERED list of rule callables (this list IS the chain)

#     def add_rule(self, rule):
#         # a rule is ANY callable rule(cart, running_total) -> new_total. Because it's just a
#         # callable, built-ins, user lambdas, and rule-classes-with-__call__ all plug in the same
#         # way (Strategy). Order of add_rule calls = order of application.
#         self.rules.append(rule)

#     def total(self, cart):
#         # THE CHAIN as a fold: start at the subtotal, then thread that number through each rule in
#         # turn — each rule's OUTPUT becomes the next rule's INPUT. E.g. 200 → 180 → 162.
#         t = cart.subtotal()
#         for rule in self.rules:
#             t = rule(cart, t)
#         # floor at 0 (a big flat discount can't make you owe money), then round money to 2 places.
#         return round(max(0, t), 2)

#     # --- built-in rule BUILDERS. Each RETURNS a rule callable (a closure). ---
#     # KEY IDEA (closure): the returned lambda "remembers" the pct/amount it was built with, so
#     # percentage(10) and percentage(20) are two different rules from the same builder.
#     @staticmethod
#     def percentage(pct):
#         # take pct% off the RUNNING total t:  t * (1 - pct/100).  10% off 180 → 180*0.9 = 162.
#         return lambda cart, t: t * (1 - pct / 100)

#     @staticmethod
#     def flat(amount):
#         # subtract a fixed amount, but not below 0 (max(0, ...) guards against over-discounting).
#         return lambda cart, t: max(0, t - amount)

#     @staticmethod
#     def threshold(min_subtotal, amount):
#         # conditional discount. NOTE: it gates on cart.subtotal() (the ORIGINAL bill), not on the
#         # already-discounted running total t — otherwise stacking discounts could sneak you under
#         # the threshold. If it qualifies → knock off `amount`; else pass t through unchanged.
#         return lambda cart, t: max(0, t - amount) if cart.subtotal() >= min_subtotal else t
