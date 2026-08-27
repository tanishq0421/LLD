# Parking Lot 🟡 Medium — the #1 most-asked LLD problem

**Format:** machine-coding + OOD · **Asked by:** Amazon, Google, Microsoft, Adobe, Uber, Grab,
Gojek · **Time budget:** 60–90 min · **Patterns:** **Strategy** (allocation + pricing),
**Factory** (spots/vehicles), Singleton (the lot manager)

> This is *the* canonical problem. Expect it to open **vague** ("Design a parking lot") to test
> your clarifying questions, then get a **concurrency escalation** ("two cars race for the last
> spot") — which is exactly the SDE-1 → SDE-2 dividing line.

---

## The prompt (as given — deliberately minimal)

> "Design a parking lot system."

That's often the entire opening line. **You** must extract the requirements by asking.

## Clarify before coding (the interviewer answers as you ask)

- What vehicle types? *"Motorcycle, Car, Truck."*
- Different spot sizes? *"Small, Medium, Large. A vehicle can use its own size or any larger one."*
- Multiple floors? *"Single lot for now; keep floors as an easy extension."*
- Pricing: flat or duration-based? *"Duration-based, per-hour rate by vehicle type, minimum 1 hour."*
- What happens when full? *"Reject the park request."*
- Do we issue tickets? *"Yes — a ticket identifies the parked vehicle for exit + billing."*

## Fit & allocation rules (agreed after clarification)

| Vehicle | Can use spot sizes |
|---|---|
| Motorcycle | Small, Medium, Large |
| Car | Medium, Large |
| Truck | Large |

**Allocation strategy:** assign the **smallest compatible free spot** (best-fit) so you don't
waste a Large spot on a motorcycle. This "which spot" decision is a **Strategy** — the interviewer
may ask you to swap it (nearest-to-entrance, floor-balancing, etc.).

## Core requirements

1. `add_spot(spot_id, spot_type)` to build the lot.
2. `park(vehicle_id, vehicle_type)` → returns a **ticket id**; raises `ParkingFull` if no
   compatible spot is free.
3. `unpark(ticket_id)` → frees the spot and returns the **fee**; raises `InvalidTicket` for a
   bad/already-used ticket.
4. `available_count(spot_type=None)` → free spots, total or by size.
5. Duration-based fee via a pluggable clock + pricing strategy.

## Follow-ups (escalations — in the order interviewers add them)

1. **Concurrency (the big one):** two cars arrive at the last compatible spot simultaneously.
   Only one must get it. *Where is the race?* (Two threads both read "spot free", both assign it.)
   Fix: **lock per spot / atomic claim**, **not** a global lock on the whole lot (a global
   `synchronized` serializes every gate and destroys throughput). Discuss optimistic vs pessimistic.
2. **Multiple floors**, and a "nearest available spot to the entrance" allocation strategy.
3. **Pricing variants:** flat vs hourly vs day-pass; free first 15 minutes — swap the pricing Strategy.
4. **Find-my-car / lot-full display board** (Observer pushing availability updates).
5. **Electric spots with charging**, handicapped spots — new spot types without editing existing code.

## Rubric

- **SDE-1:** correct park/unpark/fee, best-fit allocation, all guards, clean Vehicle/Spot/Ticket/
  Lot separation.
- **SDE-2:** allocation & pricing are swappable strategies; a **correct, fine-grained concurrency**
  story for the last-spot race; floors/new-spot-types added without touching existing classes.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
The tests inject a controllable clock so fees are deterministic — see `contract.py`.
