"""Runnable tests for the Notification System. Write solution.py first."""
import unittest

try:
    from solution import NotificationService, NotificationError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    NotificationService = NotificationError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestNotifications(unittest.TestCase):
    def setUp(self):
        self.log = []   # (channel, recipient, message)
        self.svc = NotificationService()
        self.svc.register_channel("email", lambda r, m: self.log.append(("email", r, m)))
        self.svc.register_channel("sms", lambda r, m: self.log.append(("sms", r, m)))
        self.svc.register_channel("push", lambda r, m: self.log.append(("push", r, m)))

    def test_delivers_to_subscribed_channels(self):
        self.svc.subscribe("u1", "email")
        self.svc.subscribe("u1", "sms")
        delivered = self.svc.notify("u1", "hi")
        self.assertEqual(delivered, ["email", "sms"])   # registration order
        self.assertEqual(self.log, [("email", "u1", "hi"), ("sms", "u1", "hi")])

    def test_only_subscribed_channels(self):
        self.svc.subscribe("u1", "push")
        delivered = self.svc.notify("u1", "yo")
        self.assertEqual(delivered, ["push"])
        self.assertEqual(self.log, [("push", "u1", "yo")])

    def test_no_subscription_delivers_nothing(self):
        self.assertEqual(self.svc.notify("ghost", "x"), [])
        self.assertEqual(self.log, [])

    def test_subscribe_unregistered_channel_raises(self):
        with self.assertRaises(NotificationError):
            self.svc.subscribe("u1", "whatsapp")

    def test_unsubscribe_stops_delivery(self):
        self.svc.subscribe("u1", "email")
        self.svc.subscribe("u1", "sms")
        self.svc.unsubscribe("u1", "email")
        delivered = self.svc.notify("u1", "hi")
        self.assertEqual(delivered, ["sms"])

    def test_subscribe_is_idempotent(self):
        self.svc.subscribe("u1", "email")
        self.svc.subscribe("u1", "email")
        delivered = self.svc.notify("u1", "hi")
        self.assertEqual(delivered, ["email"])   # not ["email","email"]

    def test_users_independent(self):
        self.svc.subscribe("u1", "email")
        self.svc.subscribe("u2", "sms")
        self.assertEqual(self.svc.notify("u1", "a"), ["email"])
        self.assertEqual(self.svc.notify("u2", "b"), ["sms"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
