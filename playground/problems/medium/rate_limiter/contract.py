"""
Test contract for the Rate Limiter.

Your `solution.py` must define TWO limiter classes sharing one interface `allow(client_id) -> bool`.

    class TokenBucketRateLimiter:
        def __init__(self, capacity: int, refill_rate: float, clock=None):
            # capacity   : max tokens per client bucket.
            # refill_rate: tokens added per second (may be fractional).
            # clock      : zero-arg callable returning seconds (default time.monotonic).
            # Each client starts with a FULL bucket (capacity tokens).

        def allow(self, client_id: str) -> bool:
            # Refill the client's bucket based on elapsed time (cap at capacity),
            # then consume 1 token if available. Return True if consumed, else False.

    class SlidingWindowRateLimiter:
        def __init__(self, max_requests: int, window_seconds: float, clock=None):
            # Allow at most `max_requests` per rolling `window_seconds` per client.

        def allow(self, client_id: str) -> bool:
            # Drop timestamps older than (now - window_seconds); if the remaining count
            # is < max_requests, record `now` and return True; else return False.

Both maintain independent state per client_id. Keep the read-modify-write path small — it's what
you'd guard with a lock in the concurrency follow-up.
"""
