"""Runnable tests for the Text Editor. Write solution.py first."""
import unittest

try:
    from solution import TextEditor
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    TextEditor = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestEditor(unittest.TestCase):
    def setUp(self):
        self.e = TextEditor()

    def test_type(self):
        self.e.type("hello")
        self.assertEqual(self.e.text, "hello")

    def test_type_appends(self):
        self.e.type("hello")
        self.e.type(" world")
        self.assertEqual(self.e.text, "hello world")

    def test_delete(self):
        self.e.type("hello")
        self.e.delete(3)
        self.assertEqual(self.e.text, "he")

    def test_delete_more_than_length(self):
        self.e.type("hi")
        self.e.delete(10)
        self.assertEqual(self.e.text, "")

    def test_undo_type(self):
        self.e.type("hello")
        self.e.type(" world")
        self.e.undo()
        self.assertEqual(self.e.text, "hello")

    def test_undo_delete_restores_text(self):
        self.e.type("hello")
        self.e.delete(3)          # "he"
        self.e.undo()             # restore "hello"
        self.assertEqual(self.e.text, "hello")

    def test_redo(self):
        self.e.type("hello")
        self.e.type(" world")
        self.e.undo()             # "hello"
        self.e.redo()             # "hello world"
        self.assertEqual(self.e.text, "hello world")

    def test_new_edit_clears_redo(self):
        self.e.type("hello")
        self.e.type(" world")
        self.e.undo()             # "hello"
        self.e.type("!")          # new edit -> redo stack cleared
        self.e.redo()             # no-op
        self.assertEqual(self.e.text, "hello!")

    def test_multiple_undo_redo(self):
        self.e.type("a")
        self.e.type("b")
        self.e.type("c")
        self.e.undo(); self.e.undo()      # "a"
        self.assertEqual(self.e.text, "a")
        self.e.redo()                      # "ab"
        self.assertEqual(self.e.text, "ab")

    def test_undo_empty_is_noop(self):
        self.e.undo()
        self.assertEqual(self.e.text, "")

    def test_redo_empty_is_noop(self):
        self.e.type("x")
        self.e.redo()             # nothing undone yet
        self.assertEqual(self.e.text, "x")


if __name__ == "__main__":
    unittest.main(verbosity=2)
