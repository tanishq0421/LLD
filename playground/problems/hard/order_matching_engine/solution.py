"""
ORDER MATCHING ENGINE — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Buy and sell orders arrive; an incoming order matches against the opposite side by price,
   then by arrival time; unmatched quantity rests in the book; a resting order can be cancelled."
    nouns -> OrderBook, Order (price, quantity, side, id), a price Level (a FIFO queue of orders)
    verbs -> place_order, cancel, best_bid, best_ask, open_quantity

STEP 2 — ENTITIES & RELATIONSHIPS
  OrderBook ◆──── price levels (bid side, ask side)   COMPOSITION: levels are pure book state,
                                                       owned entirely by the book.
  price level ◆──── Order (FIFO queue)                COMPOSITION: an order lives in exactly one
                                                       level's queue while resting.
  OrderBook o──── Order (self.orders index)           AGGREGATION: a flat id -> order index for
                                                       O(1) cancel / open_quantity lookups; the
                                                       SAME order object also sits in a level's
                                                       queue — one object, two ways to reach it.
  No inheritance for BUY vs SELL — they differ by which side of the book they hit and which
  comparison ("<=" vs ">=") counts as a cross; that's DATA/behavior-by-branch, not a hierarchy.

STEP 3 — PATTERN? Not a GoF pattern — the content here IS the matching algorithm:
  PRICE-TIME PRIORITY. Two independent orderings compose:
    • PRICE priority: an incoming BUY matches the LOWEST resting ask first (best price for the
      buyer); an incoming SELL matches the HIGHEST resting bid first. -> best price = best deal.
    • TIME priority: at the SAME price, whoever queued first fills first (FIFO) — a plain queue
      per price level gives this for free, no timestamps needed.
  Data structure: a heap per side gives O(log n) "what's the best price right now" (bids = max-
  heap via negation, asks = min-heap); a dict price -> deque gives O(1) FIFO within a level.
  CANCEL is lazy: mark the order's qty 0 instead of splicing it out of its deque immediately;
  every read (best_bid/best_ask/matching) skips qty<=0 orders at the front of a level and, once
  a level empties, drops its stale heap entry. Cheap writes, self-healing reads.

STEP 4 — SOLID (+ concurrency note)
  SRP   OrderBook = matching + book state. Each order is a plain dict — no behavior of its own.
  OCP   A new order type (e.g. IOC/FOK) would add branching in place_order's "rest or not"
        decision without touching the price-time matching loop itself.
  CONCURRENCY  Real exchanges process one instrument's book on a SINGLE thread (or behind one
        lock) — price-time priority is a strict ordering, and interleaving two threads' matches
        would silently corrupt fill order. Fine-grained locking doesn't help here the way it did
        for parking spots/seats: the book's cross-order sequencing IS the invariant, so it's one
        lock per book (matching engines instead scale by SHARDING one book per instrument).
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (orders arrive, cross, partially fill) ────────────
#   ob = OrderBook()
#   ob.place_order("s1", "SELL", 10, 60)        # no bids to cross -> rests: ask level 10 = [s1]
#   ob.place_order("b1", "BUY", 10, 100)        # crosses s1 @10: fills 60, 40 remains -> rests
#                                               #   -> trades = [{buy:b1, sell:s1, price:10, qty:60}]
#   ob.best_ask()                               # None (s1 fully consumed, level emptied)
#   ob.best_bid()                               # 10  (b1's leftover 40 rests)
#   ob.open_quantity("b1")                      # 40
#   ob.cancel("b1")                             # marks b1's qty 0 (lazy — still "in" the deque)
#   ob.best_bid()                               # None (best_bid's lazy cleanup skips/evicts it)
#   # Flow: place_order ALWAYS tries to match first (walking the opposite side's best price
#   # outward), then rests whatever quantity is left over — partial fill and full rest are the
#   # same code path, just with qty > 0 at the end or not.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import heapq
# from collections import deque


# class OrderBook:
#     def __init__(self):
#         self.orders = {}          # order_id -> order dict; SINGLE source of truth for its qty
#         self.bid_levels = {}      # price -> deque[order]   (BUY side, FIFO per price)
#         self.ask_levels = {}      # price -> deque[order]   (SELL side, FIFO per price)
#         self.bid_heap = []        # heap of -price  (negated so heapq's min-heap acts as max-heap)
#         self.ask_heap = []        # heap of price   (plain min-heap: lowest ask first)

#     # ---------- lazy price-level cleanup, shared by best_bid/best_ask/matching ----------
#     def _clean_top(self, heap, levels, sign):
#         # LOGIC: `sign` undoes the negation used to store bid prices (-1 for bids, +1 for asks),
#         # so `heap[0] * sign` is always the real best price for that side.
#         while heap:
#             price = heap[0] * sign
#             dq = levels.get(price)
#             if not dq:                              # level was already fully drained/removed
#                 heapq.heappop(heap)
#                 continue
#             while dq and dq[0]["qty"] <= 0:          # drop cancelled/filled orders at the FRONT
#                 dq.popleft()                         #   (FIFO: the front is always the oldest)
#             if not dq:                               # draining emptied the whole level
#                 del levels[price]
#                 heapq.heappop(heap)
#                 continue
#             return price                             # top of heap has a real, live order waiting
#         return None

#     def best_bid(self):
#         return self._clean_top(self.bid_heap, self.bid_levels, -1)

#     def best_ask(self):
#         return self._clean_top(self.ask_heap, self.ask_levels, 1)

#     def open_quantity(self, order_id):
#         order = self.orders.get(order_id)
#         return order["qty"] if order and order["qty"] > 0 else 0

#     def cancel(self, order_id):
#         # LAZY delete: just zero the quantity. The order is still physically sitting in its
#         # deque, but every reader (_clean_top) treats qty<=0 as "not really there" and evicts
#         # it the next time it's at the front. No-op for unknown ids (contract requirement).
#         order = self.orders.get(order_id)
#         if order is not None:
#             order["qty"] = 0

#     def place_order(self, order_id, side, price, quantity):
#         order = {"id": order_id, "side": side, "price": price, "qty": quantity}
#         self.orders[order_id] = order
#         if side == "BUY":
#             # a BUY crosses any ASK priced at or below what we're willing to pay
#             trades = self._match(order, self.ask_levels, self.ask_heap, 1,
#                                   lambda ask_price: ask_price <= price)
#         else:
#             # a SELL crosses any BID priced at or above what we're willing to accept
#             trades = self._match(order, self.bid_levels, self.bid_heap, -1,
#                                   lambda bid_price: bid_price >= price)
#         if order["qty"] > 0:
#             self._rest(order)          # leftover (or everything, if nothing crossed) joins the book
#         return trades

#     def _match(self, incoming, levels, heap, sign, crosses):
#         trades = []
#         while incoming["qty"] > 0:
#             top = self._clean_top(heap, levels, sign)
#             if top is None or not crosses(top):
#                 break                              # nothing left, or the best price no longer crosses
#             dq = levels[top]
#             resting = dq[0]                         # oldest order at this price = FIFO time priority
#             fill_qty = min(incoming["qty"], resting["qty"])
#             incoming["qty"] -= fill_qty
#             resting["qty"] -= fill_qty
#             # LOGIC: trades execute at the RESTING order's price (the passive side set that
#             # price first; the incoming/aggressive side just agreed to take it) — e.g. a bid
#             # resting at 11 gets hit by a sell willing to take 10 or better -> trade prints at 11.
#             buy_id = incoming["id"] if incoming["side"] == "BUY" else resting["id"]
#             sell_id = incoming["id"] if incoming["side"] == "SELL" else resting["id"]
#             trades.append({"buy_order": buy_id, "sell_order": sell_id,
#                             "price": top, "quantity": fill_qty})
#             if resting["qty"] == 0:                 # resting order fully consumed -> pop it (FIFO)
#                 dq.popleft()
#                 if not dq:
#                     del levels[top]                 # level's empty; its heap entry cleans up lazily
#         return trades

#     def _rest(self, order):
#         # remaining quantity (partial fill leftover, or a non-crossing order) joins its side's book.
#         if order["side"] == "BUY":
#             levels, heap, sign = self.bid_levels, self.bid_heap, -1
#         else:
#             levels, heap, sign = self.ask_levels, self.ask_heap, 1
#         price = order["price"]
#         if price not in levels:
#             levels[price] = deque()
#             heapq.heappush(heap, price * sign)      # first order at this price -> new heap entry
#         levels[price].append(order)                 # append = goes to the BACK of the FIFO queue
