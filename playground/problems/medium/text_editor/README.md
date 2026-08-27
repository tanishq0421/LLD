# Text Editor with Undo/Redo 🟡 Medium (Command + Memento)

**Format:** machine-coding · **Asked by:** Google, Microsoft, Adobe, and anywhere undo/redo comes up
· **Time budget:** 60 min · **Patterns:** **Command** (each edit), **Memento** (state snapshots)

> The canonical **Command / undo-redo** problem. The insight: model every edit as a reversible
> **Command** (it knows how to `execute` and `undo` itself), keep an undo stack and a redo stack, and
> undo/redo become trivial stack operations.

---

## The prompt

> "Design a text editor that supports typing text, deleting characters, and unlimited **undo** and
> **redo**. Typing appends text; delete removes the last N characters. Undo reverses the last
> operation; redo re-applies the last undone operation. Performing a new edit after an undo clears
> the redo history."

## Clarify before coding

- Cursor model or append-only? *"Append at the end + delete-from-end is enough for the core."*
- Is undo/redo unlimited? *"Yes."*
- Undo with nothing to undo? *"No-op."*
- Does a fresh edit invalidate the redo stack? *"Yes — standard editor behavior."*

## Core requirements

1. `type(text)` — append text.
2. `delete(n)` — remove the last `n` characters (capped at current length).
3. `undo()` — reverse the most recent edit (no-op if none).
4. `redo()` — re-apply the most recently undone edit (no-op if none).
5. A new `type`/`delete` after an undo **clears** the redo stack.
6. `text` — current document content.

## Why Command (+ Memento)

- **Command:** each edit is an object with `execute()` and `undo()` that captures exactly what it
  needs to reverse itself (e.g. a delete command remembers the text it removed). Undo/redo are just
  moving commands between two stacks. New edit types (replace, paste) = new command classes (OCP).
- **Memento (alternative):** snapshot the whole document before each edit and restore on undo.
  Simpler but memory-heavy for large docs. Be ready to compare the two — that trade-off is the
  discussion the interviewer wants.

## Follow-ups (escalations)

1. **Cursor + insert/delete at arbitrary positions** (not just the end).
2. **Coalescing:** merge consecutive single-char types into one undo step.
3. **Memory bound:** cap undo history; Command (deltas) vs Memento (snapshots) memory trade-off.
4. **Macros:** a composite command that groups several edits into one undo step (Composite + Command).
5. **Collaborative editing** (OT/CRDT) — where this model breaks down.

## Rubric

- **SDE-1:** correct type/delete + unlimited undo/redo, redo cleared on new edit.
- **SDE-2:** clean Command objects (undo lives with the command), articulates Command-vs-Memento
  memory trade-off, and can extend to macros/positional edits without a rewrite.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
