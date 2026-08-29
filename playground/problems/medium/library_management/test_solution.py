"""Runnable tests for the Library Management System. Write solution.py first."""
import unittest

try:
    from solution import Library, LibraryError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Library = LibraryError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


def lib():
    l = Library(max_borrow=3)
    l.add_book("isbn1", "Clean Code", copies=2)
    l.add_book("isbn2", "SICP", copies=1)
    l.add_book("isbn3", "DDIA", copies=1)
    l.add_book("isbn4", "TAOCP", copies=1)
    l.add_member("m1")
    l.add_member("m2")
    return l


class TestBorrowReturn(unittest.TestCase):
    def test_borrow_decrements(self):
        l = lib()
        l.borrow("m1", "isbn1")
        self.assertEqual(l.available("isbn1"), 1)
        self.assertEqual(l.borrowed_by("m1"), ["isbn1"])

    def test_return_increments(self):
        l = lib()
        l.borrow("m1", "isbn1")
        l.return_book("m1", "isbn1")
        self.assertEqual(l.available("isbn1"), 2)
        self.assertEqual(l.borrowed_by("m1"), [])

    def test_add_copies_stack(self):
        l = lib()
        l.add_book("isbn2", "SICP", copies=2)   # now 3 total
        self.assertEqual(l.available("isbn2"), 3)

    def test_no_copies_available(self):
        l = lib()
        l.borrow("m1", "isbn2")               # only copy
        with self.assertRaises(LibraryError):
            l.borrow("m2", "isbn2")

    def test_borrow_limit(self):
        l = lib()
        l.borrow("m1", "isbn1")
        l.borrow("m1", "isbn2")
        l.borrow("m1", "isbn3")               # at limit 3
        with self.assertRaises(LibraryError):
            l.borrow("m1", "isbn4")

    def test_no_double_borrow_same_title(self):
        l = lib()
        l.borrow("m1", "isbn1")
        with self.assertRaises(LibraryError):
            l.borrow("m1", "isbn1")

    def test_return_not_held(self):
        l = lib()
        with self.assertRaises(LibraryError):
            l.return_book("m1", "isbn1")


class TestGuards(unittest.TestCase):
    def test_unknown_member(self):
        l = lib()
        with self.assertRaises(LibraryError):
            l.borrow("ghost", "isbn1")

    def test_unknown_book(self):
        l = lib()
        with self.assertRaises(LibraryError):
            l.borrow("m1", "isbnX")
        with self.assertRaises(LibraryError):
            l.available("isbnX")

    def test_duplicate_member(self):
        l = lib()
        with self.assertRaises(LibraryError):
            l.add_member("m1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
