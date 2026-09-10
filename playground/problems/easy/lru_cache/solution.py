"""
LRU CACHE — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "A fixed-capacity key->value store; on overflow, evict whoever was used longest ago."
    nouns -> LRUCache, capacity, entry (key/value), recency order
    verbs -> get (read + mark fresh), put (write + mark fresh), evict-least-recent
  "Recency order" is not a class of its own — it's a PROPERTY of how entries are stored (an
  ordering), which is exactly what STEP 3 below turns into the data-structure choice.

STEP 2 — ENTITIES & RELATIONSHIPS
  LRUCache ◆──── entries    COMPOSITION: every (key, value) lives and dies inside the cache; there
                             is no external owner of an entry.
  NO separate Node/List classes are exposed publicly — they're an IMPLEMENTATION DETAIL of "how do
  I get O(1) recency tracking", not part of the cache's public shape. (A hand-rolled doubly linked
  list + dict is the classic from-scratch answer; Python's OrderedDict already IS that data
  structure, so we use it and name the equivalence out loud.)

STEP 3 — PATTERN? (what varies?)
  No GoF behavioural pattern applies — this is a DATA STRUCTURE problem, not a Strategy/Observer
  seam. The whole problem IS the data-structure choice: dict alone gives O(1) lookup but no order;
  a plain list gives order but O(N) reordering. The answer is dict + doubly linked list (hash map
  for O(1) key->node lookup, linked list for O(1) move-to-front / evict-from-back). Python's
  collections.OrderedDict is precisely this combo with move_to_end/popitem(last=False) built in —
  reimplementing the linked list by hand is the "show your work" version of the same idea, worth
  mentioning as the from-scratch answer even when using OrderedDict in the actual code.

STEP 4 — SOLID (+ CONCURRENCY note)
  SRP  LRUCache has exactly one job: capacity-bounded storage with recency-based eviction. get/put
       each do "one read/write + one recency bump", nothing extra.
  OCP  A different eviction POLICY (LFU, size-weighted, TTL) is a different class, not an if/else
       bolted onto this one — the class name says LRU on purpose.
  CONCURRENCY  get() and put() both mutate the shared ordering, so two threads racing a get() and a
       put() on the same key can interleave the "reorder" and "insert/evict" steps. Fix: guard the
       whole method body with a single lock (a cache is small critical sections, so one coarse
       lock is the pragmatic answer here — unlike ParkingLot's per-spot locking, over-slicing an
       LRU's lock granularity mostly adds complexity without real throughput gain).
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (object flow / a run-through) ─────────────────────
#   c = LRUCache(2)                # capacity 2, empty
#   c.put("a", 1)                  # insert a=1  -> order (oldest->newest): [a]
#   c.put("b", 2)                  # insert b=2  -> order: [a, b]
#   c.get("a")                     # 1  -> reading "a" makes it MOST recently used -> order: [b, a]
#   c.put("c", 3)                  # inserting c overflows capacity 2 -> evict LEAST recent = "b"
#                                  #   order after insert+evict: [a, c]
#   c.get("b")                     # raises KeyError -> "b" was evicted
#   len(c)                         # 2
#   # Flow: caller -> get/put (touch the entry + OrderedDict.move_to_end) -> put also checks size
#   #        and OrderedDict.popitem(last=False) to drop the front (least-recent) entry.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# from collections import OrderedDict


# class LRUCache:
#     def __init__(self, capacity):
#         if capacity < 1:
#             raise ValueError("capacity must be >= 1")
#         self.capacity = capacity
#         # LOGIC: OrderedDict remembers INSERTION order and lets us move a key to the end in O(1)
#         # (move_to_end) and pop the front in O(1) (popitem(last=False)). We use that ordering as
#         # our recency axis: front = least-recently-used, back = most-recently-used.
#         self._data = OrderedDict()

#     def get(self, key):
#         if key not in self._data:
#             raise KeyError(key)
#         # LOGIC: reading counts as "use" -> bump this key to the MRU (back) end.
#         self._data.move_to_end(key)
#         return self._data[key]

#     def put(self, key, value):
#         if key in self._data:
#             # updating an existing key also refreshes its recency
#             self._data.move_to_end(key)
#         self._data[key] = value
#         if len(self._data) > self.capacity:
#             # LOGIC: popitem(last=False) removes the FRONT item — with our convention that's the
#             # least-recently-used one (last=True would remove the most-recent, which we don't want).
#             self._data.popitem(last=False)

#     def __len__(self):
#         return len(self._data)
