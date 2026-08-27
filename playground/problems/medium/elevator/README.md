# Elevator System 🟡 Medium

**Format:** machine-coding + OOD · **Asked by:** Amazon, Microsoft, Uber, Google, Adobe, Lyft
· **Time budget:** 60–90 min · **Patterns:** **State** (elevator lifecycle), **Strategy**
(dispatch/scheduling), Observer (floor displays)

> Amazon is known to open this as "provide the APIs" and then escalate hard (multi-elevator
> dispatch, emergency mode, heartbeat/floor-sync). The base is a single elevator servicing
> requests efficiently; the SDE-2 story is the **dispatch strategy** across many.

---

## The prompt

> "Design an elevator control system. An elevator receives floor requests and must service them
> efficiently rather than naively first-come-first-served. Model the elevator's motion (moving up,
> moving down, idle) and how it decides where to go next. Support multiple elevators later."

## Clarify before coding

- One elevator or many? *"Start with one; multiple + dispatch is the follow-up."*
- Internal requests (destination buttons) only, or external (hall calls with direction) too? *"Internal to start."*
- Scheduling algorithm? *"Use LOOK/SCAN — keep moving in one direction servicing requests, then reverse."*
- Is motion time-stepped? *"Yes — model one floor per time step so it's testable."*

## Core requirements (single elevator, LOOK algorithm)

1. Elevator has `current_floor`, `direction` (`UP`/`DOWN`/`IDLE`), and a set of pending target floors.
2. `request_floor(floor)` adds a destination (validate it's within `[min_floor, max_floor]`).
3. `step()` advances one floor per call following **LOOK**: keep going in the current direction
   while there are targets ahead; when none ahead, reverse toward remaining targets; when none at
   all, go `IDLE`. Servicing a floor removes it from targets.
4. From `IDLE`, head toward the nearest requested floor.

## Model the elevator as a State machine

`IDLE`, `MOVING_UP`, `MOVING_DOWN` (and later `DOORS_OPEN`, `MAINTENANCE`, `EMERGENCY`). Each state
decides what `step()` and a new request do. This keeps the scheduling logic out of one giant
conditional and makes emergency/maintenance states pure additions.

## Follow-ups (escalations)

1. **External hall calls** (floor + desired direction) merged with internal requests.
2. **Multiple elevators + dispatch strategy:** which car answers a hall call? Nearest-car,
   least-load, or same-direction-first — a swappable **Strategy**. This is the crux of the SDE-2 bar.
3. **Emergency / maintenance states**, door open/close timing, capacity limits.
4. **Floor displays** update as the car moves — **Observer** pushing position to subscribers.
5. **Concurrency:** requests arriving while the car is moving; a central controller mediating cars.

## Rubric

- **SDE-1:** correct LOOK servicing, valid state transitions, request validation.
- **SDE-2:** clean State pattern (emergency/maintenance are additions), a pluggable multi-elevator
  dispatch Strategy, and a coherent controller + concurrency story.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
