# LLD Interview Prep — Simulate the Real Round

A practice repo for **Low-Level Design / machine-coding interviews**, tuned for the
**SDE-1 → SDE-2** transition. Each problem is presented the way an interviewer actually
presents it — a written prompt, deliberate ambiguity, and **timed follow-up escalations** —
with **runnable tests** so you can validate your own code. **No reference solutions are
included; you write those.**

> New here? Read in this order:
> 1. **[`patterns/README.md`](patterns/README.md)** — do you need all 23 GoF patterns? (No.) The high-yield tier list.
> 2. **[`HOW_TO_PRACTICE.md`](HOW_TO_PRACTICE.md)** — how to run a realistic mock round + self-scoring rubric.
> 3. **[`RESEARCH.md`](RESEARCH.md)** — the sourced evidence behind everything here (what's asked, by whom, how).
> 4. Pick a problem below and start.

---

## The 60-second answer to "what do I actually need?"

- **Patterns:** master **5** (Strategy, Observer, Factory, Singleton, State), recognize **10**, skip **8**. Design reasoning > pattern names. Over-engineering fails you.
- **Fundamentals that matter more:** SOLID, **composition over inheritance**, low coupling, restraint (KISS/YAGNI), and *narrating trade-offs*.
- **Your SDE-2 lever:** **concurrency as a follow-up** ("now make it thread-safe / two users book the same seat") + handling ambiguity and trade-offs independently.
- **How it's given:** a written/verbal prompt — **never a UML diagram to implement**. You derive the design. Machine-coding = blank IDE + runnable code; whiteboard = informal boxes/arrows + pseudocode.

---

## Problem catalog

**33 problems** (9 easy · 16 medium · 8 hard). Difficulty reflects the interview bar, not just code
size. Every problem lists the patterns it naturally invites and the concurrency escalation to expect.
Between them they cover **every Tier-1 and Tier-2 design pattern** (Strategy, Observer, Factory,
Singleton, State, Builder, Decorator, Facade, Chain of Responsibility, Adapter, Command, Template
Method, Composite, Proxy, Abstract Factory) plus **Mediator** and **Memento**, and span concurrency,
transactions, idempotency, graphs, order books, and interval modeling — see
[`patterns/README.md`](patterns/README.md) for the pattern→problem map. Problem selection is driven by
the frequency data in [`RESEARCH.md`](RESEARCH.md) and mapped to the SDE-1/SDE-2/SDE-3 question banks.

### 🟢 Easy — first-round filters / warm-ups
| Problem | Core skill | Patterns | Concurrency follow-up |
|---|---|---|---|
| [Tic-Tac-Toe](problems/easy/tic_tac_toe/README.md) | Clean board/game modeling, win-check efficiency | State-lite | (rare) |
| [Vending Machine](problems/easy/vending_machine/README.md) | The canonical **State** problem | **State**, Strategy | Concurrent dispense/refill |
| [LRU Cache](problems/easy/lru_cache/README.md) | Data-structure design (O(1) get/put) | — | Thread-safe cache |
| [Logger](problems/easy/logger/README.md) | Level routing, extensibility | **Chain of Responsibility**, Singleton | Thread-safe logging |
| [Coffee Machine](problems/easy/coffee_machine/README.md) | Compose add-ons without class explosion | **Decorator** | — |
| [Stock Ticker](problems/easy/stock_ticker/README.md) | Subject/subscriber notification | **Observer** | Notify off-thread |
| [Meal Builder](problems/easy/meal_builder/README.md) | Build complex objects w/ invariants | **Builder** | — |
| [URL Shortener](problems/easy/url_shortener/README.md) | Unique code gen + expand (≈ pastebin) | base62/Strategy, Singleton | — |
| [Voting System](problems/easy/voting_system/README.md) | One-vote invariants, live tallies | (clean modeling) | Concurrent tally |

### 🟡 Medium — the bread-and-butter machine-coding problems
| Problem | Core skill | Patterns | Concurrency follow-up |
|---|---|---|---|
| [Parking Lot](problems/medium/parking_lot/README.md) | **#1 most-asked**; allocation & pricing | **Strategy**, Factory, Singleton | Two cars race for one spot |
| [Splitwise](problems/medium/splitwise/README.md) | Command-driven, balance math, split types | **Strategy** | Concurrent expenses |
| [Snake & Ladder](problems/medium/snake_and_ladder/README.md) | Board/game orchestration, config | Factory | — |
| [Rate Limiter](problems/medium/rate_limiter/README.md) | **Concurrency-native**; token bucket / sliding window | Strategy, Singleton | Shared-counter races (core) |
| [Elevator](problems/medium/elevator/README.md) | Lifecycle + dispatch strategy | **State**, Strategy, Observer | Multi-elevator dispatch |
| [ATM](problems/medium/atm/README.md) | Auth flow + cash dispensing | **State**, **Chain of Responsibility** | Shared cash inventory |
| [Notification System](problems/medium/notification_system/README.md) | Multi-channel delivery | **Observer**, Strategy, **Adapter** | Async/retry delivery |
| [Text Editor](problems/medium/text_editor/README.md) | Unlimited undo/redo | **Command**, **Memento** | — |
| [Meeting Scheduler](problems/medium/meeting_scheduler/README.md) | Interval conflict detection | (interval modeling) | Booking race for last room |
| [Discount Engine](problems/medium/discount_engine/README.md) | Stacking promo rules | **Strategy**, **Chain of Responsibility** | — |
| [Pub/Sub Broker](problems/medium/pub_sub/README.md) | Topics + per-subscriber offsets (mini-Kafka) | **Observer** | Concurrent publish/poll (core) |
| [Online Quiz](problems/medium/online_quiz/README.md) | Attempt lifecycle + scoring | Strategy (scoring) | — |
| [Library Management](problems/medium/library_management/README.md) | Inventory + borrow invariants | (clean modeling) | Last-copy race |
| [Hotel Booking](problems/medium/hotel_booking/README.md) | Date-range reservations by room type | interval modeling | Last-room race |
| [Inventory Management](problems/medium/inventory_management/README.md) | reserve→confirm/release, no oversell | reserve/commit | Oversell race (core) |
| [Chat System](problems/medium/chat_system/README.md) | Group message fan-out | **Mediator** | Concurrent send/join |

### 🔴 Hard — SDE-2 escalations (concurrency & stateful correctness)
| Problem | Core skill | Patterns | Concurrency follow-up |
|---|---|---|---|
| [BookMyShow](problems/hard/bookmyshow/README.md) | Seat-booking **without double-booking** | Observer, State, Strategy | Two users, same seat (core) |
| [In-memory KV Store](problems/hard/inmemory_kv_store/README.md) | **Transactions**: begin/commit/rollback, nesting | Command/Memento-lite | Isolation under concurrency |
| [Ride-Hailing (Uber)](problems/hard/ride_hailing/README.md) | Rider/driver matching, trip lifecycle, pricing | Strategy, State, Observer | Concurrent match for one driver |
| [Chess](problems/hard/chess/README.md) | Polymorphic piece movement | **Factory**, polymorphism/Strategy | — |
| [File System](problems/hard/file_system/README.md) | Files/dirs as a uniform tree | **Composite** | Per-node vs subtree locking |
| [Order Matching Engine](problems/hard/order_matching_engine/README.md) | Order book, **price-time priority** | Strategy, priority structures | Serialized matching |
| [Job Scheduler](problems/hard/job_scheduler/README.md) | DAG deps, **topological sort**, cycle detection | graph modeling, Command | Parallel ready-set execution |
| [Payment Gateway](problems/hard/payment_gateway/README.md) | Payment lifecycle + **idempotency** | **State**, Strategy (providers) | Concurrent retry, exactly-once |

---

## Quick start

```bash
cd problems/medium/parking_lot
# 1) read README.md, design on paper (don't peek at the tests)
# 2) write your own solution.py exposing the entry points in contract.py
python3 -m unittest test_solution.py -v
```

Run every problem's tests at once (each in its own folder) with the helper script:

```bash
./run_tests.sh
```

It reports each problem as passing, failing, or "awaiting solution.py". Filter to one:
`./run_tests.sh parking_lot`.

Zero dependencies — everything uses the standard-library `unittest`. Python 3.10+.
(Note: `python3 -m unittest discover` from the repo root does **not** work here, because each
problem imports its own local `solution` module — always run tests from inside a problem folder,
or use `./run_tests.sh`.)

---

## A suggested 3-week plan (SDE-1 → SDE-2)

- **Week 1 — foundations + easy:** read `patterns/` + `HOW_TO_PRACTICE.md`. Do Tic-Tac-Toe,
  Vending Machine (State), LRU Cache, Logger (Chain of Responsibility). Focus: clean classes, SOLID.
- **Week 2 — the core five mediums:** Parking Lot, Splitwise, Snake & Ladder, Elevator, then
  Rate Limiter. Focus: Strategy/Factory/State in anger; start every problem with clarifying questions.
- **Week 3 — hard + concurrency pass:** BookMyShow, In-memory KV Store, Ride-Hailing. Then go
  **back** to Parking Lot / Rate Limiter / BookMyShow and do the thread-safety follow-ups properly.
  Practice narrating trade-offs aloud and timing yourself to 90 minutes.

Grade every attempt with the rubric in `HOW_TO_PRACTICE.md`.
