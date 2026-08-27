"""Runnable tests for the Pub/Sub broker. Write solution.py first."""
import unittest

try:
    from solution import Broker, PubSubError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Broker = PubSubError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestBroker(unittest.TestCase):
    def setUp(self):
        self.b = Broker()
        self.b.create_topic("orders")

    def test_publish_returns_increasing_offsets(self):
        self.assertEqual(self.b.publish("orders", "m0"), 0)
        self.assertEqual(self.b.publish("orders", "m1"), 1)
        self.assertEqual(self.b.publish("orders", "m2"), 2)

    def test_poll_returns_all_then_empty(self):
        self.b.subscribe("orders", "s1")
        self.b.publish("orders", "a")
        self.b.publish("orders", "b")
        self.assertEqual(self.b.poll("orders", "s1"), ["a", "b"])
        self.assertEqual(self.b.poll("orders", "s1"), [])   # nothing new

    def test_poll_only_new_after_first(self):
        self.b.subscribe("orders", "s1")
        self.b.publish("orders", "a")
        self.b.poll("orders", "s1")            # consumes "a"
        self.b.publish("orders", "b")
        self.assertEqual(self.b.poll("orders", "s1"), ["b"])

    def test_subscribe_gets_backlog(self):
        self.b.publish("orders", "a")
        self.b.publish("orders", "b")
        self.b.subscribe("orders", "late")     # subscribes after publishing
        self.assertEqual(self.b.poll("orders", "late"), ["a", "b"])

    def test_subscribers_independent(self):
        self.b.subscribe("orders", "s1")
        self.b.subscribe("orders", "s2")
        self.b.publish("orders", "a")
        self.assertEqual(self.b.poll("orders", "s1"), ["a"])
        self.assertEqual(self.b.poll("orders", "s2"), ["a"])   # s2 unaffected by s1's poll

    def test_duplicate_topic(self):
        with self.assertRaises(PubSubError):
            self.b.create_topic("orders")

    def test_publish_unknown_topic(self):
        with self.assertRaises(PubSubError):
            self.b.publish("ghost", "x")

    def test_poll_unknown_subscriber(self):
        with self.assertRaises(PubSubError):
            self.b.poll("orders", "nobody")


@unittest.skip("Follow-up: concurrency. Remove this skip once publish/poll are thread-safe.")
class TestConcurrency(unittest.TestCase):
    def test_concurrent_publish_unique_offsets(self):
        import threading
        b = Broker()
        b.create_topic("t")
        offsets = []
        lock = threading.Lock()

        def worker(i):
            off = b.publish("t", f"m{i}")
            with lock:
                offsets.append(off)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(200)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(sorted(offsets), list(range(200)))  # unique, gap-free


if __name__ == "__main__":
    unittest.main(verbosity=2)
