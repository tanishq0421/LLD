# Discount / Coupon Engine 🟡 Medium (Strategy + Chain of Responsibility)

**Format:** machine-coding · **Asked by:** e-commerce/fintech (Amazon, Flipkart, Swiggy, Razorpay)
· **Time budget:** 60 min · **Patterns:** **Strategy** (each discount rule), **Chain of
Responsibility** (stacking rules in order)

> Every checkout has one. The design lesson: each discount is an independent **Strategy**, and the
> engine applies a **chain** of them in order to a running total. New promo type = new strategy, no
> edits to the engine — which is exactly what a growth/promotions team needs.

---

## The prompt

> "Design a discount engine for a shopping cart. A cart has items (price × quantity). The engine
> applies a configured sequence of discount rules to compute the final total — e.g. `10% off`,
> `₹20 flat off`, `₹50 off when subtotal ≥ ₹500`. Rules stack in order, and the total never goes
> below zero. Adding a new kind of rule must not touch existing code."

## Clarify before coding

- Do rules stack, and does order matter? *"Yes and yes — apply in configured order to the running total."*
- Does a percentage apply to the original subtotal or the running (already-discounted) total? *"Running total."*
- Can the total go negative? *"Floor at 0."*
- Threshold checks original subtotal or running total? *"Original subtotal."*

## Core requirements

1. `Cart.add_item(name, price, qty)`, `Cart.subtotal()`.
2. `DiscountEngine` with `add_rule(rule)` and `total(cart)`.
3. Built-in rule builders: `percentage(pct)`, `flat(amount)`, `threshold(min_subtotal, amount)`.
4. Rules apply **in order** to the running total; result floored at 0; rounded to 2 decimals.
5. Custom rules pluggable without engine changes.

## Why these patterns

- **Strategy:** each rule is an interchangeable unit `rule(cart, running_total) -> new_total`.
  `percentage`, `flat`, `threshold`, BOGO, category-specific — all the same shape.
- **Chain of Responsibility:** the engine passes the running total through each rule in sequence; a
  rule may or may not change it (e.g. `threshold` no-ops when the subtotal is too low). Adding/removing
  a promo is reordering the chain, not editing the engine.

## Follow-ups (escalations)

1. **Non-stackable / exclusive coupons** ("best single discount wins") — the engine picks max instead of chaining.
2. **BOGO / item-level** discounts (needs the cart contents, not just the total).
3. **Caps** ("max ₹100 off"), coupon codes with validity windows and usage limits.
4. **Explainability:** return a breakdown of which rule saved how much (audit trail).
5. **Priority/ordering conflicts** between promotions — how do you make it deterministic?

## Rubric

- **SDE-1:** correct stacking in order, floor at 0, threshold logic, built-in rules.
- **SDE-2:** rules as clean Strategies (new rule = pure addition), handles exclusive-vs-stackable and
  item-level discounts, and can produce a savings breakdown.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
