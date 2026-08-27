# Logging Framework 🟢 Easy (Chain of Responsibility)

**Format:** machine-coding · **Asked by:** Amazon, Google, Microsoft, Apple, Splunk, Razorpay
("logger with labels routed by config") · **Time budget:** 40 min · **Patterns:**
**Chain of Responsibility**, Singleton (contested), Strategy (formatting)

---

## The prompt

> "Design a logging framework. It supports levels `DEBUG < INFO < WARNING < ERROR`. The logger has
> a minimum level; anything below it is ignored. A message at or above the minimum is formatted and
> emitted. Design it so new levels and new output destinations (console, file, network) can be
> added without rewriting existing code."

## Clarify before coding

- Fixed level set, or extensible? *"Start with the four; design so adding one is easy."*
- One destination or many (console + file)? *"Start with one; multiple is a follow-up."*
- Global singleton logger, or instantiable? *"Instantiable is fine; discuss singleton trade-offs."*
- Message format? *"`LEVEL: message` is fine for now; formatting should be swappable."*

## Core requirements

1. Levels ordered `DEBUG(10) < INFO(20) < WARNING(30) < ERROR(40)`.
2. A `min_level`; messages strictly below it are dropped.
3. `log(level, message)` emits a formatted record when `level >= min_level`.
4. Convenience methods: `debug/info/warning/error(message)`.

## Model it as a Chain of Responsibility (what the interviewer wants)

Build a chain of handlers, one per level (`DebugHandler → InfoHandler → WarningHandler →
ErrorHandler`). A request carries its level; each handler either handles it (if its threshold
matches) and/or forwards it down the chain. Adding a new level = inserting a link, no edits to
existing handlers (**OCP**). Contrast this with a `switch(level)` block, which you'd have to edit
for every new level.

## Follow-ups (escalations)

1. **Multiple destinations:** route `ERROR` to a file *and* console; `DEBUG` to console only. The
   chain now branches to different **sinks**.
2. **Swappable formatting** (plain / JSON / with-timestamp) — a **Strategy**.
3. **Singleton** access (`Logger.get_instance()`): implement it, then explain why DI is often
   preferred (testability, hidden dependencies).
4. **Thread-safety:** concurrent `log` calls writing to one file — what do you synchronize?
5. **Async logging:** hand off to a background queue so `log` doesn't block the caller.

## Rubric

- **SDE-1:** correct level filtering, clean formatting, convenience methods.
- **SDE-2:** genuine Chain of Responsibility (adding a level/destination edits nothing existing),
  formatting as Strategy, and coherent singleton + thread-safety trade-off discussion.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
