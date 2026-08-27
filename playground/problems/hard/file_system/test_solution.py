"""Runnable tests for the in-memory File System. Write solution.py first."""
import unittest

try:
    from solution import FileSystem, FSError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    FileSystem = FSError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestFileSystem(unittest.TestCase):
    def setUp(self):
        self.fs = FileSystem()

    def test_mkdir_and_exists(self):
        self.fs.mkdir("/a/b/c")
        self.assertTrue(self.fs.exists("/a"))
        self.assertTrue(self.fs.exists("/a/b/c"))
        self.assertFalse(self.fs.exists("/a/x"))

    def test_create_and_read_file(self):
        self.fs.mkdir("/a")
        self.fs.create_file("/a/f.txt", "hello")
        self.assertEqual(self.fs.read_file("/a/f.txt"), "hello")

    def test_create_file_missing_parent(self):
        with self.assertRaises(FSError):
            self.fs.create_file("/no/dir/f.txt", "x")

    def test_write_overwrites(self):
        self.fs.create_file("/f.txt", "old")
        self.fs.write_file("/f.txt", "new")
        self.assertEqual(self.fs.read_file("/f.txt"), "new")

    def test_ls_directory_sorted(self):
        self.fs.mkdir("/a")
        self.fs.create_file("/a/z.txt", "1")
        self.fs.create_file("/a/a.txt", "2")
        self.fs.mkdir("/a/mid")
        self.assertEqual(self.fs.ls("/a"), ["a.txt", "mid", "z.txt"])

    def test_ls_file_returns_name(self):
        self.fs.create_file("/f.txt", "x")
        self.assertEqual(self.fs.ls("/f.txt"), ["f.txt"])

    def test_size_file(self):
        self.fs.create_file("/f.txt", "hello")
        self.assertEqual(self.fs.size("/f.txt"), 5)

    def test_size_directory_recursive(self):
        self.fs.mkdir("/a/b")
        self.fs.create_file("/a/f1.txt", "abc")     # 3
        self.fs.create_file("/a/b/f2.txt", "de")    # 2
        self.assertEqual(self.fs.size("/a"), 5)

    def test_delete_file(self):
        self.fs.create_file("/f.txt", "x")
        self.fs.delete("/f.txt")
        self.assertFalse(self.fs.exists("/f.txt"))

    def test_delete_subtree(self):
        self.fs.mkdir("/a/b/c")
        self.fs.create_file("/a/b/f.txt", "x")
        self.fs.delete("/a/b")
        self.assertFalse(self.fs.exists("/a/b"))
        self.assertFalse(self.fs.exists("/a/b/c"))
        self.assertTrue(self.fs.exists("/a"))

    def test_read_missing_file(self):
        with self.assertRaises(FSError):
            self.fs.read_file("/nope.txt")

    def test_mkdir_over_file_conflicts(self):
        self.fs.create_file("/a", "x")
        with self.assertRaises(FSError):
            self.fs.mkdir("/a/b")   # "/a" is a file, can't descend


if __name__ == "__main__":
    unittest.main(verbosity=2)
