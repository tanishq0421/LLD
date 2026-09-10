"""
FILE SYSTEM — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Files and directories live in a tree; a directory holds files/directories; size of a
   directory is everything beneath it; paths are absolute and '/'-separated."
    nouns -> FileSystem, File, Directory
    verbs -> mkdir, create_file, read_file, write_file, ls, size, delete, exists

STEP 2 — ENTITIES & RELATIONSHIPS
  FileSystem ◆──── Directory (root)     COMPOSITION: the filesystem owns a single root dir;
                                        nothing outside it references that root.
  Directory ◆──── File / Directory      COMPOSITION: a directory owns its children (a name ->
                                        node map); delete a directory, its whole subtree dies
                                        with it. Children never outlive their parent.
  File and Directory are BOTH "nodes" but we don't need a shared abstract base class in Python —
  duck typing + isinstance checks are enough at this size. (In Java/C++ you'd define an FSNode
  interface with size(); that's the textbook Composite.)

STEP 3 — PATTERN? COMPOSITE.
  What varies: a path component can be a FILE (leaf, holds content, size = len(content)) or a
  DIRECTORY (composite, holds children, size = sum of children's sizes). Composite lets client
  code call `.size()` on ANY node — file or directory — without asking "which kind is this?"
  first; the recursion (directory delegates to each child) IS the pattern's whole point.

STEP 4 — SOLID (+ concurrency note)
  SRP   File = a name + content. Directory = a name + a map of children. FileSystem = path
        parsing/navigation and the public API — none of that logic lives inside File/Directory.
  OCP   A new node kind (e.g. a symlink) would slot in as another type with its own .size();
        FileSystem's path-walking code doesn't change.
  LSP   Anywhere the code expects "a node with a name", either File or Directory works.
  CONCURRENCY  Two threads racing "mkdir -p /a/b" and "delete /a" is the real-world danger — a
        walk in progress can see a directory vanish mid-traversal. Fix: a lock per-directory
        around child-map mutation (or one coarse lock over the whole tree if traffic is low);
        never mutate a dict while another thread iterates it unlocked.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (build a small tree, then inspect it) ─────────────
#   fs = FileSystem()                          # root "/" starts as an empty directory
#   fs.mkdir("/a/b")                           # mkdir -p: creates "a" then "b" under it
#   fs.create_file("/a/f1.txt", "abc")         # parent "/a" exists -> file "f1.txt" (size 3)
#   fs.create_file("/a/b/f2.txt", "de")        # parent "/a/b" exists -> file "f2.txt" (size 2)
#   fs.ls("/a")                                # ["b", "f1.txt"]           (sorted child names)
#   fs.size("/a")                              # 5   (3 from f1.txt + 2 from f2.txt under b/, recursive)
#   fs.write_file("/a/f1.txt", "abcdef")       # overwrite -> size becomes 6
#   fs.delete("/a/b")                          # drops the whole "b" subtree (and f2.txt with it)
#   fs.exists("/a/b")                          # False
#   # Flow: every call splits the path into components and WALKS the tree from root, one dict
#   # lookup per component — that walk is the one piece of logic every method reuses.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# class FSError(Exception):
#     pass


# class _File:
#     # LEAF of the Composite: holds content, no children. size() is the base case of the recursion.
#     def __init__(self, name, content=""):
#         self.name = name
#         self.content = content

#     def size(self):
#         return len(self.content)


# class _Directory:
#     # COMPOSITE node: holds a name -> node map (children can be _File or _Directory).
#     def __init__(self, name):
#         self.name = name
#         self.children = {}   # child name -> _File | _Directory

#     def size(self):
#         # LOGIC: a directory's size is the SUM of its children's sizes, and each child answers
#         # with ITS OWN .size() — if that child is itself a directory, its .size() recurses again.
#         # Example: /a has f1.txt(3) and dir b/ containing f2.txt(2) -> size(/a) = 3 + size(b)
#         #        = 3 + 2 = 5. Neither FileSystem nor _Directory needs to know how deep it goes;
#         # the recursion bottoms out at _File.size(), which just returns len(content).
#         return sum(child.size() for child in self.children.values())


# class FileSystem:
#     def __init__(self):
#         self.root = _Directory("")   # the root "/" starts as an empty directory

#     # ---------- path helpers ----------
#     def _parts(self, path):
#         # "/a/b/c" -> ["a","b","c"]; "/" -> [] (empty list means "the root itself").
#         return [p for p in path.split("/") if p]

#     def _lookup(self, path):
#         # Walk from root through each path component. Every hop must land on an EXISTING
#         # directory before we can descend further, or the path doesn't exist.
#         node = self.root
#         for part in self._parts(path):
#             if not isinstance(node, _Directory) or part not in node.children:
#                 raise FSError(f"no such path: {path}")
#             node = node.children[part]
#         return node

#     def _parent_dir(self, parts):
#         # Walk to the directory that SHOULD contain parts[-1] (used by create_file/delete).
#         # Reuses the exact same walk as _lookup, just stopping one component short.
#         node = self.root
#         for part in parts[:-1]:
#             if not isinstance(node, _Directory) or part not in node.children:
#                 raise FSError("parent directory does not exist")
#             node = node.children[part]
#         if not isinstance(node, _Directory):
#             raise FSError("parent is not a directory")
#         return node

#     # ---------- public API ----------
#     def mkdir(self, path):
#         # mkdir -p: create every missing component along the way, reusing ones that already exist.
#         node = self.root
#         for part in self._parts(path):
#             if not isinstance(node, _Directory):
#                 raise FSError(f"{part}: parent is a file, cannot descend")
#             child = node.children.get(part)
#             if child is None:
#                 child = _Directory(part)          # missing -> create it
#                 node.children[part] = child
#             elif not isinstance(child, _Directory):
#                 raise FSError(f"{part} exists and is a file")   # e.g. mkdir /a/b when /a is a FILE
#             node = child

#     def create_file(self, path, content=""):
#         parts = self._parts(path)
#         if not parts:
#             raise FSError("cannot create a file at the root path")
#         parent = self._parent_dir(parts)          # FSError if parent missing/not a directory
#         name = parts[-1]
#         parent.children[name] = _File(name, content)   # create OR overwrite (contract allows both)

#     def read_file(self, path):
#         node = self._lookup(path)
#         if not isinstance(node, _File):
#             raise FSError(f"{path} is not a file")
#         return node.content

#     def write_file(self, path, content):
#         node = self._lookup(path)
#         if not isinstance(node, _File):
#             raise FSError(f"{path} is not a file")
#         node.content = content

#     def ls(self, path):
#         node = self._lookup(path)
#         if isinstance(node, _File):
#             return [node.name]                    # ls on a file just names itself
#         return sorted(node.children.keys())        # ls on a directory -> sorted child names

#     def size(self, path):
#         # LOGIC: dispatch to whichever node we found — File or Directory both expose .size(),
#         # so the caller never has to branch on the node's type (that's the Composite payoff).
#         return self._lookup(path).size()

#     def delete(self, path):
#         parts = self._parts(path)
#         if not parts:
#             raise FSError("cannot delete the root")
#         parent = self._parent_dir(parts)
#         name = parts[-1]
#         if name not in parent.children:
#             raise FSError(f"no such path: {path}")
#         del parent.children[name]                  # drops the node; if it's a directory, its
#         # entire children dict goes with it (Python GC's the whole subtree) -> subtree delete
#         # is a ONE-LINE dict deletion, no manual recursive walk needed.

#     def exists(self, path):
#         try:
#             self._lookup(path)
#             return True
#         except FSError:
#             return False
