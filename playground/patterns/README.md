# Design Patterns for LLD Interviews — High-Yield Tier List

> **Bottom line:** You do **not** need all 23 GoF patterns. Master **5**, recognize **10**,
> skim **8**. Interviewers reward *good design reasoning* (SOLID, composition, restraint),
> not pattern name-dropping. Reaching for 3+ patterns in one problem is usually a red flag.

This guide is the "theory" half of the repo. The `problems/` folder is the practice half.
Study a pattern **together with the problem it naturally solves** — that's how it sticks.

---

## Tier 1 — Master these 5 (they cover most interviews)

| Pattern | One-line intent | Canonical LLD problems | Practice in |
|---|---|---|---|
| **Strategy** | Swap an algorithm/behavior at runtime behind one interface | Payment methods, pricing/allocation rules, discount engine, chess move rules | `parking_lot`, `splitwise`, `discount_engine`, `rate_limiter` |
| **Observer** | Notify many dependents when one subject changes | Notifications, pub/sub, order-status updates, stock ticker | `stock_ticker`, `notification_system`, `pub_sub` |
| **Factory** (usually *Simple Factory*) | Centralize object creation; caller doesn't `new` concrete types | Vehicle/piece/notification creation | `parking_lot`, `snake_and_ladder`, `chess` |
| **Singleton** | One shared instance with a global access point | Logger, config, central manager | `logger`, `rate_limiter` |
| **State** | Object changes behavior when its internal state changes | Vending machine, elevator, ATM, order lifecycle | `vending_machine`, `elevator`, `atm` |

> ⚠️ **"Factory" in interviews almost always means *Simple Factory*** (a `create(type)` method),
> not the GoF *Factory Method* (subclass-overridden creators). Don't overcomplicate it.
>
> ⚠️ **Singleton is contested.** Know it, but also know the criticism: it hides dependencies
> and hurts testability. Saying "I'd use a Singleton here, though dependency injection is
> cleaner for testing" is an SDE-2 signal.

---

## Tier 2 — Recognize the shape, reach when it fits (10)

| Pattern | Intent | Canonical problem | Practice in |
|---|---|---|---|
| **Builder** | Construct complex objects step-by-step (many optional fields) | Meal/PC/HTTP-request customization | `meal_builder` |
| **Decorator** | Add responsibilities dynamically by wrapping | Pizza/coffee toppings, notification enrichment | `coffee_machine` |
| **Facade** | One simple interface over a complex subsystem | Checkout facade, coordinating many services | *(discussed in `notification_system`)* |
| **Chain of Responsibility** | Pass a request along handlers until one handles it | ATM cash dispenser, logging levels, approval flow | `logger`, `atm`, `discount_engine` |
| **Adapter** | Make an incompatible interface usable | Wrapping a legacy/third-party payment gateway | `notification_system` |
| **Command** | Encapsulate a request as an object (queue/undo it) | Text-editor undo/redo, remote control, job queue | `text_editor` |
| **Template Method** | Fixed algorithm skeleton, pluggable steps | Report pipelines, game-turn processing | *(job execution in `job_scheduler`)* |
| **Composite** | Treat individual + groups of objects uniformly (trees) | File system, org hierarchy, menu systems | `file_system` |
| **Proxy** | Stand-in that controls access to another object | Caching proxy, access control, lazy loading | *(LRU as a cache layer; discuss)* |
| **Abstract Factory** | Create families of related objects | Cross-platform UI kit, themed component families | *(rare — sketch only)* |

> **Memento** (Tier 3) also gets real practice in `text_editor` (undo via snapshots) and
> `inmemory_kv_store` (transaction rollback). **Iterator/Flyweight/Mediator/Visitor/Prototype/Bridge/
> Interpreter** stay skim-only — recognize and name them, don't over-invest.

---

## Tier 3 — Skim, only if explicitly asked (8)

| Pattern | Intent | When it appears |
|---|---|---|
| **Flyweight** | Share immutable state to save memory | Text-editor glyphs, board pieces, "optimize memory" probes |
| **Iterator** | Traverse a collection without exposing internals | Rarely hand-rolled — languages give you this |
| **Mediator** | Central hub decouples many-to-many objects | Chat room, air-traffic control |
| **Memento** | Capture/restore state without breaking encapsulation | Undo snapshots, game saves |
| **Visitor** | Add operations to a stable object structure | AST processing, tax/discount over order types |
| **Prototype** | Clone expensive-to-build objects | Post-DB-fetch caching + clone |
| **Bridge** | Decouple abstraction from implementation | Device/remote, shape/renderer |
| **Interpreter** | Evaluate a simple grammar/DSL | Tiny expression languages (<20 rules) |

---

## What matters MORE than patterns (interviewers weight this heavily)

1. **SOLID** — taught by example, not memorized definitions:
   - **S**RP: one reason to change per class.
   - **O**CP: open for extension, closed for modification (add a class, don't edit existing ones).
   - **L**SP: subclasses substitutable without callers special-casing them.
   - **I**SP: many small focused interfaces > one fat interface.
   - **D**IP: depend on abstractions; inject dependencies via the constructor (testability).
2. **Composition over inheritance** — *"In most LLD interviews you don't need inheritance at all.
   Inheritance is where candidates get into trouble."* Compose small focused objects instead.
3. **Coupling & cohesion** — Law of Demeter: avoid `a.getB().getC().getD()` chains.
4. **Restraint (KISS / YAGNI)** — start with the simplest thing that works; let patterns
   *emerge* from pain points. Patterns should arise from design decisions, not drive them.
5. **Trade-off articulation** — say the alternatives out loud (pessimistic vs optimistic locking,
   inheritance vs composition, sync vs async). *"A design you can't explain is indistinguishable
   from a bad one."*

---

## Recommended learning order (pattern ↔ problem, reinforced together)

**Phase 0 — foundations (before any pattern):**
OOP basics → class relationships (association / aggregation / composition / dependency) →
DRY, KISS, YAGNI, Law of Demeter → SOLID → UML class diagrams.

**Phase 1 — one pattern per problem:**

| # | Pattern | Paired problem (in this repo) |
|---|---|---|
| 1 | *(warm-up, force no pattern)* | `parking_lot` — practice requirement-gathering + class design |
| 2 | **Strategy** | `parking_lot` pricing/allocation, or `splitwise` split types |
| 3 | **Observer** | `notification_system` / `bookmyshow` status updates |
| 4 | **Factory + Singleton** | `snake_and_ladder` / `logger` |
| 5 | **State** | `vending_machine` → `elevator` |
| 6 | **Decorator** | (coffee/pizza — see notes) |
| 7 | **Chain of Responsibility** | `logger` levels / ATM dispenser |
| 8 | **Command** | text-editor undo/redo |
| 9 | **Composite / Facade / Template** | file system / checkout |
| 10 | **Builder / Abstract Factory** | complex construction |
| **Final** | **Concurrency pass** | revisit `parking_lot`, `rate_limiter`, `bookmyshow` and add thread-safety |

**Why problem-first:** you only *feel* why Strategy matters after an `if/else` explosion in a
real payment design. Studying patterns abstractly from the GoF catalog doesn't transfer to the room.

---

## Sources
Hello Interview (patterns, principles, concurrency, prep), Educative (frequently-asked patterns),
CodeZym (4 most-important patterns; 7-day roadmap), AlgoMaster (learn-LLD-from-zero; pattern guides),
`ashishps1/awesome-low-level-design` (GitHub). See the top-level `RESEARCH.md` for full links.
