# Coffee Machine / Beverage Customization 🟢 Easy (Decorator pattern)

**Format:** machine-coding warm-up · **Asked as:** the canonical **Decorator** teaching problem
(coffee/pizza toppings) · **Time budget:** 30–40 min · **Patterns:** **Decorator**

> The classic problem for learning **Decorator**. The trap is a combinatorial explosion of classes
> (`EspressoWithMilk`, `EspressoWithMilkAndSugar`, …) or a pile of boolean flags. Decorator lets you
> *wrap* a beverage with add-ons, composing cost and description at runtime.

---

## The prompt

> "Model a coffee shop. There are base beverages (espresso, latte, cappuccino) each with a price,
> and add-ons (milk, sugar, caramel) each with an extra price. A customer builds a drink by starting
> from a base and adding any number of add-ons in any combination. Compute the total cost and a
> description like `Espresso, Milk, Sugar`. Adding a new add-on must not require touching existing code."

## Clarify before coding

- Can an add-on be applied more than once (double milk)? *"Yes — allow repeats."*
- Order in the description? *"Base first, then add-ons in the order added."*
- Fixed menu or extensible? *"Extensible — adding a beverage/add-on should be trivial."*

## Core requirements

1. Base beverages with prices: `espresso 2.0`, `latte 3.0`, `cappuccino 3.5`.
2. Add-ons with prices: `milk 0.5`, `sugar 0.25`, `caramel 0.75`.
3. `cost()` returns base + sum of add-ons; `description()` returns `Base, AddonA, AddonB` in order.
4. Add-ons compose (any number, repeats allowed).
5. Unknown base/add-on → error.

## Why Decorator (the design point)

Each add-on is a **decorator** that wraps a `Beverage` and overrides `cost()`/`description()` by
delegating to the wrapped object and adding its own bit. A new add-on = one new decorator class, no
edits elsewhere (**OCP**). Compare with the `boolean has_milk, has_sugar…` approach, which forces you
to edit the cost method every time.

## Follow-ups (escalations)

1. **Sizes** (small/medium/large) that scale the base *and* some add-ons — where does that fit?
2. **Discounts** on the final drink (another decorator, or a separate step?).
3. A **menu/price sheet** that's data-driven so non-engineers can add drinks.
4. Contrast Decorator vs Strategy vs plain composition — when is Decorator *over*-engineering?

## Rubric

- **SDE-1:** correct cost + description, add-ons compose, unknown items rejected.
- **SDE-2:** genuine Decorator (new add-on = pure addition), and can articulate when a simpler
  data-driven approach would beat Decorator.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
