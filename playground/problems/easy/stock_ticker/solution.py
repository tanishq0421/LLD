"""
STOCK PRICE TICKER — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "A stock has a price; interested parties subscribe to be told when it changes."
    nouns -> Stock (subject), Observer (anything with an `update` method)
    verbs -> subscribe, unsubscribe, set_price -> notify
  "Observer" is not a concrete class here — Python duck-types it: ANY object with
  `update(symbol, old_price, new_price)` qualifies. No ABC required at this scale.

STEP 2 — ENTITIES & RELATIONSHIPS
  Stock o──── Observer×N     AGGREGATION: the stock holds REFERENCES to observers it does not
                             own or create — they're built and passed in by the caller, and
                             outlive (or can outlive) their subscription.
  Stock ───▶ Observer.update ASSOCIATION: Stock depends only on the `update(...)` SHAPE, never on
                             a concrete Recorder/Dashboard/Logger class (dependency INVERSION —
                             the subject depends on an interface, not on implementations).
  NO inheritance: Stock isn't a kind of anything, and observers aren't a family under Stock — two
  unrelated hierarchies connected only by a protocol.

STEP 3 — PATTERN? (what varies?)
  WHAT varies: the set of parties that care when price changes, and what each one does about it
  (log it, redraw a UI, fire an alert). Classic Observer: subject holds a list of observers and
  pushes updates; new observer types plug in with zero changes to Stock. This IS the textbook
  home for Observer — no simpler shape fits "one-to-many, react-on-change" better.

STEP 4 — SOLID (+ concurrency note)
  SRP   Stock owns price state + the subscriber list; it does NOT know what a Recorder or
        Dashboard does with a notification — that logic lives in the observer.
  OCP   Add a new kind of observer (SMS alert, chart) by writing a new class with `update()`;
        Stock's code never changes.
  DIP   Stock depends on the abstract `update()` shape, not on any concrete observer type.
  CONCURRENCY  If set_price() is called from multiple threads, two racing writers could both
        read the "old" price before either notifies, corrupting the old->new deltas observers
        see. Fix: guard the read-compare-write-notify sequence with a lock.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (object flow / a run-through) ─────────────────────
#   aapl = Stock("AAPL", 100.0)          # subject starts at $100
#   dash = Dashboard(); log = Logger()   # two unrelated observer types
#   aapl.subscribe(dash); aapl.subscribe(log)   # both registered; list = [dash, log]
#   aapl.subscribe(dash)                 # idempotent: dash already present -> no duplicate
#   aapl.set_price(101.0)                # 100 != 101 -> notify all: dash.update(...), log.update(...)
#   aapl.price                           # 101.0
#   aapl.unsubscribe(log)                # log removed; dash still subscribed
#   aapl.set_price(101.0)                # UNCHANGED value -> no notification to anyone
#   # Flow: caller -> Stock.set_price -> compare old/new -> (if changed) loop subscribers -> each observer.update(...)
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# class Stock:
#     def __init__(self, symbol, price):
#         self._symbol = symbol
#         self._price = price
#         # LOGIC: a list (not a set) preserves subscribe ORDER for deterministic notify order,
#         # while we still dedupe manually in subscribe() via an explicit "already in?" check.
#         self._observers = []

#     @property
#     def symbol(self):
#         return self._symbol

#     @property
#     def price(self):
#         return self._price

#     def subscribe(self, observer):
#         # IDEMPOTENT: only append if this exact object isn't already registered, so calling
#         # subscribe() twice with the same observer never produces two notifications per change.
#         if observer not in self._observers:
#             self._observers.append(observer)

#     def unsubscribe(self, observer):
#         # LOGIC: unknown observer -> no-op. `list.remove` would raise ValueError on a missing
#         # item, so we guard with an `in` check first rather than try/except — clearer intent.
#         if observer in self._observers:
#             self._observers.remove(observer)

#     def set_price(self, new_price):
#         if new_price == self._price:
#             return  # no real change -> no notification (tested: test_no_notify_when_unchanged)
#         old_price = self._price
#         self._price = new_price
#         # PUSH model: Stock actively calls each observer with the full delta (symbol, old, new).
#         # Observers don't mutate the subscriber list mid-notify in this simple version, so a
#         # plain loop is safe; if unsubscribe-during-notify were needed we'd loop over a copy.
#         for observer in self._observers:
#             observer.update(self._symbol, old_price, new_price)
