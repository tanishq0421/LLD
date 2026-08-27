"""
Test contract for the in-memory File System (Composite).

Your `solution.py` must define `FileSystem` and an `FSError` exception. Paths are absolute,
"/"-separated, e.g. "/a/b/file.txt". The root is "/".

    class FileSystem:
        def __init__(self):
            # Starts with an empty root directory "/".

        def mkdir(self, path: str) -> None:
            # Create the directory and any missing parents (like `mkdir -p`).
            # FSError if a path component exists as a FILE.

        def create_file(self, path: str, content: str = "") -> None:
            # Create/overwrite a file. Parent directory must already exist (FSError otherwise).

        def read_file(self, path: str) -> str:
            # File content. FSError if missing or not a file.

        def write_file(self, path: str, content: str) -> None:
            # Overwrite an existing file's content. FSError if missing or not a file.

        def ls(self, path: str) -> list:
            # Directory -> sorted list of child names. File -> [basename]. FSError if missing.

        def size(self, path: str) -> int:
            # File -> len(content). Directory -> sum of sizes of everything beneath it.

        def delete(self, path: str) -> None:
            # Remove a file or a whole directory subtree. FSError if missing. (Cannot delete "/".)

        def exists(self, path: str) -> bool: ...

Implement files and directories as a Composite tree with a shared node interface.
"""
