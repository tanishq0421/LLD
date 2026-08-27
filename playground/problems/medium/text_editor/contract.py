"""
Test contract for the Text Editor (Command + Memento).

Your `solution.py` must define `TextEditor`:

    class TextEditor:
        def __init__(self): ...

        def type(self, text: str) -> None:
            # Append `text` to the document. Clears the redo history.

        def delete(self, n: int) -> None:
            # Remove the last min(n, len) characters. Clears the redo history.

        def undo(self) -> None:
            # Reverse the most recent type/delete. No-op if there is nothing to undo.

        def redo(self) -> None:
            # Re-apply the most recently undone edit. No-op if there is nothing to redo.

        @property
        def text(self) -> str:
            # Current document content.

Implement with the Command pattern (each edit knows how to undo itself) and/or Memento snapshots.
"""
