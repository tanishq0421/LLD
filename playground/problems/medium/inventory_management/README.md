# Inventory Management (E-commerce) 🟡 Medium (concurrency)

**Format:** machine-coding + concurrency · **Asked by:** Amazon, Flipkart, e-commerce/logistics
· **Time budget:** 60 min · **Patterns:** reserve/commit lifecycle; concurrency (the point)

> The core of every checkout. The key idea is **reserve → confirm/release**: you hold stock while a
> customer checks out (so two customers can't oversell the last unit), then either commit it on
> payment or release it on timeout/abandon. The last-unit race is the SDE-2 signal.

---

## The prompt

> "Design an inventory system for e-commerce. Each product (SKU) has a stock count. When a customer
> starts checkout, **reserve** the quantity so no one else can take it; on payment **confirm** it
> (removes from stock); on abandon/timeout **release** it back. `available` = on-hand minus what's
> currently reserved. Support restocking."

## Clarify before coding

- Difference between on-hand and available? *"available = on_hand − reserved. Reserving doesn't remove
  stock; confirming does."*
- Reservation timeout/auto-release? *"Model release explicitly; auto-expiry via a clock is a follow-up."*
- Reserve more than available? *"Reject."*
- What must never happen? *"Overselling — two reservations for stock that isn't there."*

## Core requirements

1. `add_product(sku, quantity)`, `restock(sku, qty)`.
2. `available(sku)` → `on_hand − reserved`.
3. `reserve(sku, qty)` → `reservation_id`; reject if `available < qty` (`InventoryError`).
4. `confirm(reservation_id)` — commit: reduce on-hand by the reserved qty; reservation done.
5. `release(reservation_id)` — return the reserved qty to available; reservation done.
6. Double confirm/release or unknown reservation → error.

## The concurrency requirement (the point)

Two checkouts call `reserve(sku, 1)` for the last unit at the same instant. A naive
check-then-decrement lets both succeed → oversell. You must guarantee **at most `available`** total
reservations. Guard the read-modify-write per SKU (lock per product, or atomic decrement / CAS).
A single global lock is correct but serializes every SKU — discuss **per-SKU** locking.

## Follow-ups (escalations)

1. **Reservation TTL:** auto-release holds after N minutes (inject a clock + a reaper).
2. **Multi-item carts:** reserve several SKUs atomically (all-or-nothing across products).
3. **Warehouses/locations:** stock split across sites; allocation strategy.
4. **Backorders / safety stock / reorder points** (Observer on low stock).
5. **Distributed inventory:** the atomic decrement moves to the DB/Redis at scale.

## Rubric

- **SDE-1:** correct reserve/confirm/release accounting, available = on_hand − reserved, guards.
- **SDE-2:** names the oversell race precisely, implements **per-SKU** thread-safety, and sketches
  TTL holds, multi-item atomic reservation, and the distributed version.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
The concurrency stress test is **skipped by default** — enable it once `reserve` is thread-safe.
