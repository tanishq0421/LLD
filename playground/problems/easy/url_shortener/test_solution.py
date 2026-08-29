"""Runnable tests for the URL Shortener. Write solution.py first."""
import unittest

try:
    from solution import URLShortener, AliasTaken
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    URLShortener = AliasTaken = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestShortener(unittest.TestCase):
    def setUp(self):
        self.s = URLShortener()

    def test_round_trip(self):
        code = self.s.shorten("https://example.com/a/b/c")
        self.assertEqual(self.s.expand(code), "https://example.com/a/b/c")

    def test_codes_are_unique(self):
        c1 = self.s.shorten("https://a.com")
        c2 = self.s.shorten("https://b.com")
        self.assertNotEqual(c1, c2)
        self.assertEqual(self.s.expand(c1), "https://a.com")
        self.assertEqual(self.s.expand(c2), "https://b.com")

    def test_custom_alias(self):
        self.s.shorten("https://example.com", alias="promo")
        self.assertEqual(self.s.expand("promo"), "https://example.com")

    def test_alias_collision(self):
        self.s.shorten("https://a.com", alias="dup")
        with self.assertRaises(AliasTaken):
            self.s.shorten("https://b.com", alias="dup")

    def test_expand_unknown(self):
        with self.assertRaises(KeyError):
            self.s.expand("nope")

    def test_delete(self):
        code = self.s.shorten("https://a.com")
        self.s.delete(code)
        with self.assertRaises(KeyError):
            self.s.expand(code)

    def test_delete_unknown(self):
        with self.assertRaises(KeyError):
            self.s.delete("ghost")

    def test_same_url_twice_two_codes(self):
        c1 = self.s.shorten("https://same.com")
        c2 = self.s.shorten("https://same.com")
        self.assertNotEqual(c1, c2)
        self.assertEqual(self.s.expand(c1), "https://same.com")
        self.assertEqual(self.s.expand(c2), "https://same.com")


if __name__ == "__main__":
    unittest.main(verbosity=2)
