"""Runnable tests for the Chat System. Write solution.py first."""
import unittest

try:
    from solution import ChatServer, ChatError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    ChatServer = ChatError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestChat(unittest.TestCase):
    def setUp(self):
        self.s = ChatServer()
        self.s.create_room("r1")
        for u in ("alice", "bob", "carol"):
            self.s.join("r1", u)

    def test_fanout_excludes_sender(self):
        recipients = self.s.send("r1", "alice", "hello")
        self.assertEqual(recipients, ["bob", "carol"])

    def test_history_records(self):
        self.s.send("r1", "alice", "hi")
        self.s.send("r1", "bob", "yo")
        self.assertEqual(self.s.history("r1"), [("alice", "hi"), ("bob", "yo")])

    def test_members_sorted(self):
        self.assertEqual(self.s.members("r1"), ["alice", "bob", "carol"])

    def test_non_member_cannot_send(self):
        with self.assertRaises(ChatError):
            self.s.send("r1", "dave", "intruder")

    def test_leave_stops_delivery(self):
        self.s.leave("r1", "bob")
        recipients = self.s.send("r1", "alice", "hi")
        self.assertEqual(recipients, ["carol"])

    def test_join_idempotent(self):
        self.s.join("r1", "alice")   # already a member
        self.assertEqual(self.s.members("r1"), ["alice", "bob", "carol"])

    def test_unknown_room(self):
        with self.assertRaises(ChatError):
            self.s.send("ghost", "alice", "hi")
        with self.assertRaises(ChatError):
            self.s.join("ghost", "alice")

    def test_duplicate_room(self):
        with self.assertRaises(ChatError):
            self.s.create_room("r1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
