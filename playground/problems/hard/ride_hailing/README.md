# Ride-Hailing (Uber / Ola) 🔴 Hard

**Format:** LLD + HLD hybrid · **Asked by:** Uber, Ola, Lyft, and as a general "design a matching
system" problem · **Time budget:** 75–90 min · **Patterns:** **Strategy** (matching + pricing),
**State** (trip lifecycle), Observer (driver/rider notifications)

> Broad by design — you must **scope it down** fast (a common SDE-2 test of driving ambiguity).
> The core LLD is: match a rider to a driver, run the trip through its states, price it. The
> concurrency twist ("two riders matched to the same driver") mirrors the seat-booking race.

---

## The prompt

> "Design the core of a ride-hailing service. Riders request rides from a pickup location; the
> system assigns a nearby available driver. A trip goes through request → assigned → ongoing →
> completed (or cancelled), and is charged a fare based on distance. Design the matching and the
> trip lifecycle."

## Clarify before coding (scope it down!)

- In scope: matching, trip lifecycle, fare. Out of scope: maps/routing, payments, GPS streaming,
  surge across a whole city? *"Yes — focus on match + lifecycle + fare. Assume simple coordinates."*
- Matching rule? *"Nearest available driver for now; make it swappable."*
- Locations? *"2D integer coordinates; use Manhattan distance."*
- What must never happen? *"One driver assigned to two active trips at once."*

## Core requirements

1. `register_driver(driver_id, x, y)` — a driver available at a location.
2. `request_ride(rider_id, x, y)` — match the **nearest available** driver, mark them busy, create a
   trip in `ASSIGNED`; return `trip_id`. Raise `NoDriverAvailable` if none free.
3. Trip lifecycle via `start_trip` (ASSIGNED→ONGOING) and `end_trip(trip_id, drop_x, drop_y)`
   (ONGOING→COMPLETED, returns fare, frees the driver at the drop location).
4. `cancel_trip` (from ASSIGNED or ONGOING → CANCELLED, frees the driver).
5. Invalid transitions raise `InvalidTrip`; unknown ids raise `KeyError`.
6. **Fare** = pricing strategy over pickup→drop distance (default `base 50 + 10×distance`).

## Design as State + Strategy

- **Trip state machine:** `REQUESTED/ASSIGNED → ONGOING → COMPLETED | CANCELLED`. Each transition is
  guarded; illegal ones raise. This is the **State** pattern — and it's what keeps `end_trip` from
  silently working on a cancelled trip.
- **Matching strategy** (nearest / highest-rated / lowest-ETA) and **pricing strategy** (flat /
  per-distance / surge) are swappable **Strategies**. Interviewers love swapping these live.

## Follow-ups (escalations)

1. **Concurrency:** two riders request at the same time and the nearest driver is the same person —
   only one trip may get them. Same check-then-act race as seat booking; guard the match-and-assign.
2. **Surge pricing** by demand/supply in an area (pricing Strategy variant).
3. **Driver rejects / times out** → re-match to the next-nearest (matching becomes a small workflow).
4. **Spatial indexing** for nearest-driver at scale (grid/quadtree/geohash) instead of scanning all drivers.
5. **Notifications** to rider and driver on each state change (**Observer**).

## Rubric

- **SDE-1:** correct matching, full trip lifecycle with guarded transitions, fare, driver freed on
  end/cancel.
- **SDE-2:** scopes the problem down decisively, matching & pricing as clean Strategies, a correct
  concurrency story for the double-assignment race, and a sketch of spatial indexing at scale.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
The concurrency stress test is **skipped by default** — enable it once matching is thread-safe.
