# Stock Price Ticker 🟢 Easy (Observer pattern)

**Format:** machine-coding warm-up / OOD · **Asked as:** the canonical **Observer** teaching problem
(stock ticker / weather station) · **Time budget:** 30–40 min · **Patterns:** **Observer**

> The cleanest way to learn **Observer** before you meet it inside bigger problems (notifications,
> pub/sub, order-status updates). A subject (`Stock`) holds state; many observers react when it
> changes — without the subject knowing anything concrete about them.

---

## The prompt

> "A stock has a symbol and a price. Various displays/apps want to be notified whenever the price
> changes so they can react. Design it so any number of subscribers can register and unregister, and
> each is notified on a price change — but the stock must not depend on the concrete subscriber types."

## Clarify before coding

- Notify on every `set_price`, or only when the value actually changes? *"Only on a real change."*
- Can the same observer subscribe twice? *"Treat subscribe as idempotent — no duplicate notifications."*
- Push the new value to observers, or let them pull it? *"Push (symbol, old, new)."*

## Core requirements

1. `Stock(symbol, price)` with a current `price`.
2. `subscribe(observer)` / `unsubscribe(observer)` — observers implement `update(symbol, old, new)`.
3. `set_price(new)` updates the price and notifies all observers **only if the value changed**.
4. Unsubscribed observers stop receiving updates; unknown unsubscribe is a no-op.

## Why Observer (the design point)

The `Stock` keeps a list of observers and calls a common `update(...)` on each — it depends on the
**observer interface**, never on concrete display classes. Adding a new kind of subscriber (mobile
app, alerting service) requires **zero** changes to `Stock` (**OCP** + loose coupling). This is the
same shape you'll reuse in notification systems, pub/sub, and MVC.

## Follow-ups (escalations)

1. **Many stocks:** a `Market` managing symbols; observers subscribe per symbol.
2. **Push vs pull:** send only "something changed" and let observers pull details — trade-offs?
3. **Ordering / re-entrancy:** an observer that (un)subscribes *during* notification — how do you
   avoid mutating the list you're iterating?
4. **Async / thread-safety:** notifications delivered off the writer's thread (bridges into pub/sub).

## Rubric

- **SDE-1:** correct subscribe/unsubscribe/notify, notify-only-on-change.
- **SDE-2:** safe iteration under (un)subscribe-during-notify, and a clear push-vs-pull + async story.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
