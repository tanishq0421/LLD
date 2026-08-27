# In-memory Pub/Sub (Message Broker) 🟡 Medium (Observer + concurrency)

**Format:** machine-coding / concurrency design · **Asked by:** Razorpay ("in-memory pub-sub:
producer/consumer/subscription/offset"), and general messaging-system rounds · **Time budget:**
60–75 min · **Patterns:** **Observer** (fan-out), producer/consumer, offset tracking (mini-Kafka)

> A step up from the stock-ticker Observer: instead of push callbacks, this is a **pull** broker with
> **topics** and a **per-subscriber offset** — the mental model behind Kafka. Each consumer reads at
> its own pace and never loses its place. The concurrency follow-up is where it earns "medium+".

---

## The prompt

> "Design an in-memory publish/subscribe message broker. Producers publish messages to a named topic.
> Consumers subscribe to a topic and poll for messages they haven't seen yet. Each subscriber tracks
> its own position (offset) independently, so two subscribers to the same topic both receive every
> message, at their own pace."

## Clarify before coding

- Push (broker calls consumer) or pull (consumer polls)? *"Pull, with per-subscriber offsets."*
- Does a new subscriber get the backlog or only future messages? *"Backlog — start at offset 0 (earliest)."*
- Are messages retained forever? *"In-memory retain-all for the base; retention/compaction is a follow-up."*
- Delivery semantics? *"At-least-once-ish; poll advances the offset."*

## Core requirements

1. `create_topic(topic)` (error on duplicate).
2. `publish(topic, message)` → the 0-based **offset** assigned; error on unknown topic.
3. `subscribe(topic, subscriber)` — start at offset 0.
4. `poll(topic, subscriber)` → the list of messages not yet consumed by that subscriber, and advance
   its offset. A second poll with no new messages returns `[]`.
5. Subscribers have **independent** offsets (both get all messages).

## Why Observer / offsets

Publishing fans a message out to all subscribers of a topic (**Observer**), but decoupled in time:
the broker stores the log and each subscriber holds a cursor. This is what lets consumers be slow,
restart, or replay — the difference between a toy Observer and a real message queue.

## Follow-ups (escalations)

1. **Concurrency (core):** concurrent `publish` must assign unique, gap-free offsets; concurrent
   `poll` must not double-deliver or skip. Where do you lock? (Per-topic append + per-subscriber cursor.)
2. **Consumer groups:** several consumers share a topic's partitions, each message to one group member.
3. **Retention / compaction / max size**; **replay** from a given offset (`seek`).
4. **Push variant** with backpressure; **ack/nack** and redelivery on failure.
5. **Partitions** for parallelism and ordering-per-key.

## Rubric

- **SDE-1:** correct topics, increasing offsets, per-subscriber independent polling, backlog on subscribe.
- **SDE-2:** thread-safe publish/poll (unique offsets, no double-deliver), and a clear story for
  consumer groups, retention, and replay.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
The concurrency stress test is **skipped by default** — enable it once publish/poll are thread-safe.
