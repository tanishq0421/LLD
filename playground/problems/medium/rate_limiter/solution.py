"""
RATE LIMITER — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Given a client id, decide allow/deny based on a configured limit. Token bucket first, sliding
   window as a swap-in. Limits are per-client."
    nouns -> Bucket (tokens + last-refill-time, per client), TimestampLog (per client), Limiter
    verbs -> allow

STEP 2 — ENTITIES & RELATIONSHIPS
  TokenBucketRateLimiter ◆──── per-client bucket state   COMPOSITION: each limiter owns a
                                                          dict of client_id -> [tokens, last_ts];
                                                          a bucket has no meaning outside its limiter.
  SlidingWindowRateLimiter ◆──── per-client timestamp log  same idea: client_id -> [ts, ts, ...].
  *RateLimiter o──── clock                                DEPENDENCY INJECTION: time is PASSED IN
                                                          (`clock or time.monotonic`), never read
                                                          via a bare time.monotonic() call buried
                                                          in allow() — that's what makes refill /
                                                          window math testable with a fake clock.
  NO inheritance between the two limiters (and none needed) — they don't share an implementation,
  only a SHAPE: both expose `allow(client_id) -> bool`. That shared shape is the whole contract;
  Python's duck typing means no ABC is required to swap one for the other at a call site.

STEP 3 — PATTERN? (what varies?)
  Strategy (the algorithm). TokenBucketRateLimiter and SlidingWindowRateLimiter are two
  interchangeable "is this request allowed?" algorithms behind one interface `allow(client_id)`.
  A gateway that holds `self.limiter = TokenBucketRateLimiter(...)` can swap it for the sliding
  window version without changing a single call site — that's the whole point of naming this
  Strategy rather than "two unrelated classes that happen to look similar."

STEP 4 — SOLID + CONCURRENCY (concurrency-native — this IS the problem, not a follow-up)
  SRP   each limiter only decides allow/deny for its own algorithm; the clock is someone else's
        problem (injected), not something the limiter manufactures.
  OCP   a third algorithm (leaky bucket, fixed window) is a new class with the same `allow` shape.
  CONCURRENCY — THE core of this problem, not a bolt-on:
    `allow()` is a classic READ-MODIFY-WRITE: read the bucket's tokens, compute a new value,
    write it back (same shape for the sliding window's read-log/append-write). If two threads
    call allow("shared") at the same instant on a bucket holding 1 token:
        thread A reads tokens=1 ─┐
        thread B reads tokens=1 ─┤  both still see "1 left" before either writes back
        thread A: 1>=1 -> allow, writes tokens=0
        thread B: 1>=1 -> allow, writes tokens=0        <- WRONG: 2 requests allowed on 1 token
    This is a LOST UPDATE, the same race as `count += 1` from two threads. Fix: guard the
    read-modify-write with a lock — but scope it to ONE CLIENT's bucket (e.g. a
    `defaultdict(threading.Lock)` keyed by client_id), never a single lock around the whole
    limiter. A global lock would serialize client "a" behind client "z" — correct, but it turns
    an O(1)-per-client operation into a single queue for every tenant, which defeats the purpose
    of per-client limits at any real scale. This test is SKIPPED below (`TestConcurrency`) — the
    unlocked version demonstrably over-allows under threads; adding `threading.Lock()` per client
    around the read-modify-write in `allow()` is the fix, and un-skipping that test is how you'd
    prove it.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (burst, drain, refill — with an injected clock) ───
#   clk = Clock(0)                                  # injected fake clock (real code: omit -> time.monotonic)
#   rl = TokenBucketRateLimiter(capacity=3, refill_rate=1, clock=clk)
#   rl.allow("c1")                                   # True  (bucket starts full: 3 -> 2)
#   rl.allow("c1"); rl.allow("c1")                    # True, then False (2->1->0, then empty)
#   clk.t = 2.0                                       # 2 seconds pass
#   rl.allow("c1")                                    # True  (refilled 2*1=2 tokens, capped at 3 -> consume 1 -> 1 left)
#   sw = SlidingWindowRateLimiter(max_requests=2, window_seconds=10, clock=clk)
#   sw.allow("c1"); sw.allow("c1")                    # True, True  (2 timestamps recorded at t=2.0)
#   sw.allow("c1")                                    # False (3rd request within the same 10s window)
#   clk.t = 12.0                                      # both old timestamps now outside the window
#   sw.allow("c1")                                    # True
#   # Flow: allow() -> read this client's state (lazy-init on first sight) -> recompute against
#   #       `clock()` -> allow-or-deny -> write state back. That's the section a lock would wrap.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import time


# class TokenBucketRateLimiter:
#     def __init__(self, capacity, refill_rate, clock=None):
#         self.capacity = capacity
#         self.refill_rate = refill_rate          # tokens added per second
#         self.clock = clock or time.monotonic
#         # LOGIC: client_id -> [tokens, last_refill_ts]. Lazily created on first `allow()` so
#         # there's no separate "register client" call — the spec says buckets start FULL, so we
#         # can't pre-populate without knowing every client id in advance.
#         self.buckets = {}

#     def allow(self, client_id):
#         now = self.clock()
#         if client_id not in self.buckets:
#             # LOGIC: brand-new client starts with a FULL bucket, "last refilled" right now (so
#             # the very next refill computes elapsed=0, not a huge bogus gap from epoch/monotonic 0).
#             self.buckets[client_id] = [self.capacity, now]
#         tokens, last = self.buckets[client_id]
#         # LOGIC: refill = however many seconds passed * tokens/second, added to what's left, but
#         # never above capacity (a bucket can't overflow). Example: capacity=3, 2 tokens left,
#         # 100 seconds pass at 1/s -> would be 102, capped back down to 3.
#         elapsed = now - last
#         tokens = min(self.capacity, tokens + elapsed * self.refill_rate)
#         if tokens >= 1:
#             tokens -= 1          # consume one token for this request
#             allowed = True
#         else:
#             allowed = False       # bucket empty -> throttle
#         # write back EVERY time (even on deny) so `last` always reflects "as of now" -- otherwise
#         # a burst of denied calls would each recompute the same stale elapsed time.
#         self.buckets[client_id] = [tokens, now]
#         return allowed


# class SlidingWindowRateLimiter:
#     def __init__(self, max_requests, window_seconds, clock=None):
#         self.max_requests = max_requests
#         self.window_seconds = window_seconds
#         self.clock = clock or time.monotonic
#         self.logs = {}           # client_id -> list of request timestamps still "in window"

#     def allow(self, client_id):
#         now = self.clock()
#         cutoff = now - self.window_seconds
#         log = self.logs.setdefault(client_id, [])
#         # LOGIC: drop every timestamp older than the window — a request from 11s ago doesn't
#         # count against a 10s window anymore. Rebuilding the list is the "read" half of R-M-W.
#         log[:] = [ts for ts in log if ts >= cutoff]
#         if len(log) < self.max_requests:
#             log.append(now)      # record this request -> the "write" half of R-M-W
#             return True
#         return False
