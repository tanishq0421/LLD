# Order Matching Engine (Stock Exchange) 🔴 Hard

**Format:** machine-coding / concurrency design · **Asked by:** Goldman Sachs, Morgan Stanley,
Coinbase, Robinhood, Google (fintech/trading orgs) · **Time budget:** 75–90 min · **Patterns:**
Strategy (matching policy), priority structures; correctness under **price-time priority**

> The defining fintech LLD problem. It's less about GoF patterns and more about getting the
> **matching rules exactly right**: price priority, then time (FIFO) priority, partial fills, and
> trades executing at the **resting (passive) order's price**. Precision matters — an off-by-one in
> priority is a real bug.

---

## The prompt

> "Design a limit order book for a single instrument. Traders place BUY or SELL limit orders with a
> price and quantity. An incoming order matches against the opposite side by **price-time priority**:
> a BUY matches the lowest-priced sells at or below its price; a SELL matches the highest-priced buys
> at or above its price; within a price level, oldest orders fill first. Support partial fills; any
> unfilled remainder rests in the book. Report the trades each order generates."

## Clarify before coding

- Limit orders only, or market orders too? *"Limit for the base; market orders are a follow-up."*
- Execution price when a BUY at 11 meets a resting SELL at 10? *"At the resting (passive) order's price — 10."*
- Partial fills allowed? *"Yes."*
- Priority? *"Price first, then time (FIFO) within a price level."*

## Core requirements

1. `place_order(order_id, side, price, quantity)` → the list of **trades** it generated (possibly empty).
   A trade is `{"buy_order", "sell_order", "price", "quantity"}`.
2. Matching by **price-time priority**; trades execute at the **resting** order's price.
3. **Partial fills:** a partially filled resting order stays with reduced quantity; an incoming order
   keeps matching until filled or no more crossing orders, then rests.
4. `best_bid()` / `best_ask()` → best prices, or `None` if that side is empty.
5. `open_quantity(order_id)` → quantity still resting (0 if filled/cancelled/unknown).
6. `cancel(order_id)` → remove a resting order.

## Design hints

Two sides: **bids** (buys, matched high→low) and **asks** (sells, matched low→high). Each price level
is a FIFO queue (time priority). A heap or sorted map keyed by price gives you the best level quickly;
the FIFO queue gives time priority within it. Keep an `order_id → order` index for `cancel` and
`open_quantity`. Nouns → `Order`, `PriceLevel`, `OrderBook`, `Trade`.

## Follow-ups (escalations)

1. **Market orders** (no price — take whatever's available), **IOC/FOK** (immediate-or-cancel / fill-or-kill).
2. **Concurrency:** a single matching thread (seqlock) vs locking — why exchanges often serialize matching.
3. **Efficiency:** O(log n) best-price access at scale; cancel in O(1) with intrusive lists.
4. **Multiple instruments**, order modification (cancel-replace keeps or loses time priority?).
5. **Self-trade prevention**, fees, and an audit log of every trade.

## Rubric

- **SDE-1:** correct crossing, partial fills, resting remainder, best bid/ask, cancel.
- **SDE-2:** exact **price-time priority** (FIFO within a level), trades at the passive price, multiple
  price levels matched in order, and a clear efficiency + concurrency (serialized matching) story.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
