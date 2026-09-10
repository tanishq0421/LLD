"""
PUB/SUB BROKER — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Producers publish to a named topic; consumers subscribe and poll for what they haven't seen;
  each subscriber tracks its own position."
    nouns -> Broker, Topic(log), Subscriber(offset) ; verbs -> create_topic, publish, subscribe, poll

STEP 2 — ENTITIES & RELATIONSHIPS
  Broker ◆──── Topic           COMPOSITION: topics live and die inside the broker (create_topic).
  Topic ◆──── Message log       COMPOSITION: the append-only list of published messages belongs
                               to that topic alone — it's not shared, not referenced elsewhere.
  Topic o──── Subscriber offset AGGREGATION: a subscriber's CURSOR (an int) is state the topic
                               tracks on the subscriber's behalf, but the subscriber (a plain
                               string id here) exists independently of the topic's bookkeeping.
  NO inheritance: there's one kind of topic and one kind of subscriber in the base — they differ
  by DATA (name, offset), not behaviour.

STEP 3 — PATTERN? (what varies?)
  This IS Observer, but the PULL variant: a naive push-Observer calls every watcher synchronously
  on publish() — one slow/dead subscriber blocks or crashes the publisher, and a subscriber that
  was offline misses messages forever. Instead the broker just APPENDS to a log (source of truth)
  and each subscriber holds an independent OFFSET into it; poll() is "give me everything past my
  cursor, then move my cursor." That decoupling — store once, replay per-reader at your own pace
  — is the whole idea behind Kafka. What varies here isn't a swappable algorithm so much as WHO
  owns the read position: the broker owns the log, each subscriber owns only an int.

STEP 4 — SOLID + CONCURRENCY
  SRP  Topic-log growth (publish) and per-subscriber progress (poll) are separate concerns; the
       Broker just coordinates topic lookup and subscriber registration.
  OCP  a consumer-groups feature (message goes to ONE member of a group, not all) adds a new
       registration type without touching publish()'s append logic.
  CONCURRENCY (the core follow-up, tested by a SKIPPED thread-stress test — TestConcurrency in
       test_solution.py): 200 threads call publish() at once. Without a lock, two threads can both
       read `len(log)` as the same value, both append, and BOTH return the same offset — a
       collision, and the log now has messages in an order that doesn't match the offsets handed
       out (a GAP-producing race, since one write silently overwrites the "slot" the other thread
       thought it claimed only in the sense of returned offset). The fix: one `threading.Lock`
       guarding "read current length, append, return that length" as a SINGLE atomic step, scoped
       per TOPIC (not one global broker lock, which would serialise publishes across unrelated
       topics and kill throughput). poll() needs the same discipline: read-offset + slice +
       advance-offset must happen atomically per (topic, subscriber), else a publish landing
       mid-poll could be read twice or dropped. Using ONE lock per topic for both publish and
       poll keeps it simple and correct; splitting further (per-subscriber lock for poll) is the
       next-level answer if profiling shows the per-topic lock contends.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (publish, two independent subscribers) ────────────
#   b = Broker()
#   b.create_topic("orders")
#   b.publish("orders", "order#1")             # log=["order#1"] -> offset 0
#   b.subscribe("orders", "billing")           # billing starts at offset 0 (sees the backlog)
#   b.publish("orders", "order#2")             # log=["order#1","order#2"] -> offset 1
#   b.poll("orders", "billing")                # ["order#1","order#2"]; billing's offset -> 2
#   b.poll("orders", "billing")                # []  (nothing new since offset 2)
#   b.subscribe("orders", "analytics")         # joins late, offset 0 -> still sees the FULL backlog
#   b.poll("orders", "analytics")              # ["order#1","order#2"]  (independent of billing's cursor)
#   # Flow: publish() appends to the topic's shared log and returns the new offset; poll() is
#   # purely a per-subscriber READ — it never mutates the log, only that subscriber's cursor.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import threading


# class PubSubError(Exception):
#     pass


# class Broker:
#     def __init__(self):
#         self.topics = {}       # topic -> [message, ...]      the append-only log (source of truth)
#         self.offsets = {}      # topic -> {subscriber: next_offset_to_read}
#         # LOGIC: one lock PER TOPIC, not one lock for the whole broker — publishes/polls on
#         # "orders" shouldn't wait behind publishes/polls on an unrelated topic "payments".
#         self.locks = {}        # topic -> threading.Lock

#     def create_topic(self, topic):
#         if topic in self.topics:
#             raise PubSubError(f"topic already exists: {topic}")
#         self.topics[topic] = []
#         self.offsets[topic] = {}
#         self.locks[topic] = threading.Lock()

#     def publish(self, topic, message):
#         if topic not in self.topics:
#             raise PubSubError(f"unknown topic: {topic}")
#         # LOGIC: "read current length, append, return that length" is the critical section.
#         # Two threads racing here without a lock could both read len==5, both append (log now has
#         # 7 entries at indices 5 and 6), and both return offset 5 — a duplicate, non-unique offset.
#         # The lock makes read-length + append one atomic step, so offsets stay unique and gap-free
#         # even under the 200-thread stress test (see STEP 4).
#         with self.locks[topic]:
#             offset = len(self.topics[topic])
#             self.topics[topic].append(message)
#             return offset

#     def subscribe(self, topic, subscriber):
#         if topic not in self.topics:
#             raise PubSubError(f"unknown topic: {topic}")
#         # LOGIC: start at 0 -> poll() will hand back the entire existing log on first call, i.e.
#         # a late subscriber still gets the full backlog (contract requirement).
#         self.offsets[topic][subscriber] = 0

#     def poll(self, topic, subscriber):
#         if topic not in self.topics or subscriber not in self.offsets[topic]:
#             raise PubSubError(f"unknown topic/subscriber: {topic}/{subscriber}")
#         # LOGIC: same lock as publish() — this makes "read my offset, slice new messages, advance
#         # my offset to the end" one atomic step relative to concurrent publish()es on this topic,
#         # so a message can't be both missed (offset advanced past it before it's read) and can't
#         # be double-delivered (offset advanced twice for the same slice).
#         with self.locks[topic]:
#             start = self.offsets[topic][subscriber]
#             log = self.topics[topic]
#             new_messages = log[start:]           # everything this subscriber hasn't consumed yet
#             self.offsets[topic][subscriber] = len(log)   # cursor jumps to the current end
#             return new_messages
