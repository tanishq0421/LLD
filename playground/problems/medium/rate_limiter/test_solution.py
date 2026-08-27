"""Runnable tests for the Rate Limiter. Write solution.py first."""
import unittest

try:
    from solution import TokenBucketRateLimiter, SlidingWindowRateLimiter
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    TokenBucketRateLimiter = SlidingWindowRateLimiter = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class Clock:
    def __init__(self, t=0.0):
        self.t = t
    def __call__(self):
        return self.t


class TestTokenBucket(unittest.TestCase):
    def test_burst_up_to_capacity(self):
        clk = Clock(0)
        rl = TokenBucketRateLimiter(capacity=3, refill_rate=1, clock=clk)
        self.assertTrue(rl.allow("c1"))
        self.assertTrue(rl.allow("c1"))
        self.assertTrue(rl.allow("c1"))
        self.assertFalse(rl.allow("c1"))  # bucket empty

    def test_refill_over_time(self):
        clk = Clock(0)
        rl = TokenBucketRateLimiter(capacity=3, refill_rate=1, clock=clk)
        for _ in range(3):
            rl.allow("c1")           # drain
        self.assertFalse(rl.allow("c1"))
        clk.t = 1.0                   # 1 second -> 1 token
        self.assertTrue(rl.allow("c1"))
        self.assertFalse(rl.allow("c1"))

    def test_refill_caps_at_capacity(self):
        clk = Clock(0)
        rl = TokenBucketRateLimiter(capacity=3, refill_rate=1, clock=clk)
        rl.allow("c1")                # 2 left
        clk.t = 100.0                 # would refill 100, but caps at 3
        self.assertTrue(rl.allow("c1"))
        self.assertTrue(rl.allow("c1"))
        self.assertTrue(rl.allow("c1"))
        self.assertFalse(rl.allow("c1"))

    def test_clients_are_independent(self):
        clk = Clock(0)
        rl = TokenBucketRateLimiter(capacity=1, refill_rate=1, clock=clk)
        self.assertTrue(rl.allow("a"))
        self.assertFalse(rl.allow("a"))
        self.assertTrue(rl.allow("b"))  # b has its own bucket


class TestSlidingWindow(unittest.TestCase):
    def test_within_limit(self):
        clk = Clock(0)
        rl = SlidingWindowRateLimiter(max_requests=2, window_seconds=10, clock=clk)
        self.assertTrue(rl.allow("c1"))
        self.assertTrue(rl.allow("c1"))
        self.assertFalse(rl.allow("c1"))

    def test_window_slides(self):
        clk = Clock(0)
        rl = SlidingWindowRateLimiter(max_requests=2, window_seconds=10, clock=clk)
        rl.allow("c1")     # t=0
        rl.allow("c1")     # t=0
        clk.t = 11         # both old requests now outside the 10s window
        self.assertTrue(rl.allow("c1"))

    def test_partial_slide(self):
        clk = Clock(0)
        rl = SlidingWindowRateLimiter(max_requests=2, window_seconds=10, clock=clk)
        rl.allow("c1")     # t=0
        clk.t = 5
        rl.allow("c1")     # t=5  -> 2 in window
        self.assertFalse(rl.allow("c1"))
        clk.t = 11         # t=0 request expires, t=5 still in window
        self.assertTrue(rl.allow("c1"))

    def test_clients_are_independent(self):
        clk = Clock(0)
        rl = SlidingWindowRateLimiter(max_requests=1, window_seconds=10, clock=clk)
        self.assertTrue(rl.allow("a"))
        self.assertFalse(rl.allow("a"))
        self.assertTrue(rl.allow("b"))


@unittest.skip("Follow-up: thread-safety. Remove this skip after adding per-client locking.")
class TestConcurrency(unittest.TestCase):
    def test_no_overallow_under_threads(self):
        import threading
        # 200 threads race for a bucket of 50 tokens (no refill). Exactly 50 must succeed.
        rl = TokenBucketRateLimiter(capacity=50, refill_rate=0, clock=lambda: 0)
        allowed = []
        lock = threading.Lock()

        def worker():
            ok = rl.allow("shared")
            if ok:
                with lock:
                    allowed.append(1)

        threads = [threading.Thread(target=worker) for _ in range(200)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(sum(allowed), 50)  # a naive (non-locked) limiter over-allows here


if __name__ == "__main__":
    unittest.main(verbosity=2)
