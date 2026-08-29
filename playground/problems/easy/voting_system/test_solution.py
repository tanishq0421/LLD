"""Runnable tests for the Voting System. Write solution.py first."""
import unittest

try:
    from solution import VotingSystem, VotingError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    VotingSystem = VotingError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestVoting(unittest.TestCase):
    def setUp(self):
        self.v = VotingSystem()
        self.v.create_poll("p1", "Best language?", ["python", "java", "go"])

    def test_vote_and_results(self):
        self.v.vote("p1", "u1", "python")
        self.v.vote("p1", "u2", "python")
        self.v.vote("p1", "u3", "go")
        self.assertEqual(self.v.results("p1"), {"python": 2, "java": 0, "go": 1})

    def test_one_vote_per_voter(self):
        self.v.vote("p1", "u1", "python")
        with self.assertRaises(VotingError):
            self.v.vote("p1", "u1", "java")

    def test_invalid_option(self):
        with self.assertRaises(VotingError):
            self.v.vote("p1", "u1", "rust")

    def test_unknown_poll(self):
        with self.assertRaises(VotingError):
            self.v.vote("ghost", "u1", "python")
        with self.assertRaises(VotingError):
            self.v.results("ghost")

    def test_closed_poll_rejects_votes(self):
        self.v.vote("p1", "u1", "python")
        self.v.close_poll("p1")
        with self.assertRaises(VotingError):
            self.v.vote("p1", "u2", "go")

    def test_duplicate_poll(self):
        with self.assertRaises(VotingError):
            self.v.create_poll("p1", "again?", ["a", "b"])

    def test_empty_options(self):
        with self.assertRaises(VotingError):
            self.v.create_poll("p2", "no options", [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
