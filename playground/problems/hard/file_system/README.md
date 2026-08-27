# In-memory File System 🔴 Hard (Composite pattern)

**Format:** machine-coding · **Asked by:** Amazon, Google, Microsoft; a common "hard" tier problem
· **Time budget:** 60–75 min · **Patterns:** **Composite** (files + directories as a uniform tree)

> The textbook **Composite** problem: a directory contains files *and* other directories, and you
> treat a leaf (file) and a composite (directory) through the same interface. Once the tree is right,
> `size`, `ls`, and `delete` become simple recursions.

---

## The prompt

> "Design an in-memory file system. Support creating directories (like `mkdir -p`), creating and
> reading files with content, listing a directory, computing sizes (a file's size is its content
> length; a directory's size is the sum of everything under it), and deleting paths. Paths look like
> `/a/b/c`."

## Clarify before coding

- `mkdir` create intermediate dirs (`-p`)? *"Yes."*
- Does `create_file` create missing parent dirs? *"No — parent must exist, else error."*
- `write_file` append or overwrite? *"Overwrite for the base."*
- `ls` on a file? *"Return just that file's name (LeetCode-style); on a directory, sorted child names."*

## Core requirements

1. `mkdir(path)` — create the directory and any missing parents.
2. `create_file(path, content)` — parent dir must exist; overwrite if it already exists.
3. `read_file(path)` / `write_file(path, content)`.
4. `ls(path)` — sorted child names for a directory; `[basename]` for a file.
5. `size(path)` — file = `len(content)`; directory = sum of all descendants.
6. `delete(path)` — remove a file or an entire subtree.
7. `exists(path)`. Errors on missing paths / type mismatches (`FSError`).

## Why Composite

A `Directory` and a `File` share a common node interface with a `size()` operation. `File.size()`
returns its content length; `Directory.size()` returns the sum of its children's `size()` — the
recursion is uniform because the tree is uniform. `ls`, `delete`, and traversal follow the same
shape. This is Composite's whole reason to exist: **treat individual objects and compositions of
objects identically.**

## Follow-ups (escalations)

1. **Search/glob** (`find`, wildcard matching) over the tree.
2. **Permissions / ownership**, symlinks (careful: symlinks break the pure tree into a graph).
3. **Move/copy** subtrees; hard links.
4. **In-place edits & offsets** (seek/append at position); a real block/inode model.
5. **Concurrency:** many threads mutating the tree; lock granularity per node vs per subtree.

## Rubric

- **SDE-1:** correct mkdir -p, file create/read/write, ls, recursive size, delete.
- **SDE-2:** clean Composite (File/Directory share an interface, recursions are uniform), sensible
  error handling, and a story for search/permissions/concurrency.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
