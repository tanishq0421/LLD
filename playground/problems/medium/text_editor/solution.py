"""
TEXT EDITOR — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Type appends text; delete removes from the end; undo/redo walk that history back and forth."
    nouns -> TextEditor, document text, an edit history ; verbs -> type, delete, undo, redo

STEP 2 — ENTITIES & RELATIONSHIPS
  TextEditor ◆──── undo stack ◆──── edits    COMPOSITION: the history lives and dies with the
                                              editor; an edit outside its editor is meaningless.
  TextEditor ◆──── redo stack                same composition — it's just "future" history.
  NO inheritance for edit kinds (type vs delete) — they differ by a tag + payload, not by
  polymorphic behaviour worth a class hierarchy at this scale (see STEP 3 for why we still
  keep the Command IDEA without building two Command classes).

STEP 3 — PATTERN? (what varies?)
  COMMAND: every edit must know how to UNDO itself. We represent an edit as a tiny
  (kind, payload) record instead of a TypeCommand/DeleteCommand class pair — same idea (each
  edit carries what it needs to invert itself), lighter machinery. Name the seam: "if edits grew
  more kinds (replace, move-cursor) I'd promote these tuples to real Command objects with
  execute()/undo() methods."
  MEMENTO (the key trick that makes undo trivial here): delete always removes from the TAIL, so
  the "memento" an edit needs to save is just the substring it affected —
    • type("abc")   -> undo = drop the last 3 chars       (the memento IS the typed text)
    • delete(3)     -> undo = re-append the removed chars (the memento IS the deleted text)
  Both inverses are pure string-slicing — no need to snapshot the whole document each edit.
  UNDO/REDO STACK MECHANICS (the actual crux of this problem):
    - undo() pops the undo stack, inverts that edit, and PUSHES it onto the redo stack (so redo
      can re-apply the exact same edit forward).
    - Any NEW edit (type/delete) must clear the redo stack — once you've branched into new
      history, the old "future" (what you undid) is no longer reachable. This is why
      test_new_edit_clears_redo exists: undo, then type something new, and the old redo is gone.

STEP 4 — SOLID (+ complexity note)
  SRP   TextEditor owns text + both stacks; the undo/redo LOGIC (invert-and-swap-stacks) is
        identical for every edit kind, so it lives in one place per direction, not duplicated.
  OCP   a new edit kind just needs a ("kind", payload) tuple and one extra branch in undo/redo —
        type()/delete() themselves don't change.
  COMPLEXITY  type/delete/undo/redo are all O(1) amortized (Python string slicing off the tail is
        cheap relative to the string's own storage); a rope/gap-buffer would matter for a huge
        document with mid-string edits, which this problem doesn't ask for.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (type, undo, redo, then branch history) ───────────
#   e = TextEditor()
#   e.type("hello")                            # text="hello"; undo=[("type","hello")]; redo=[]
#   e.type(" world")                            # text="hello world"; undo has both edits
#   e.undo()                                    # pop ("type"," world") -> drop last 6 chars
#   e.text                                      # "hello"           ; redo=[("type"," world")]
#   e.redo()                                    # pop redo, re-append " world"
#   e.text                                      # "hello world"
#   e.undo()                                    # back to "hello" again; redo=[("type"," world")]
#   e.type("!")                                 # NEW edit -> redo CLEARED; text="hello!"
#   e.redo()                                    # no-op: nothing left to redo
#   e.text                                      # "hello!"
#   # Flow: type/delete push (kind, payload) onto undo + wipe redo; undo pops undo -> inverts ->
#   # pushes onto redo; redo pops redo -> re-applies -> pushes back onto undo.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# class TextEditor:
#     def __init__(self):
#         self._text = ""
#         self._undo = []     # list of ("type", inserted_str) | ("delete", removed_str)
#         self._redo = []     # same shape; holds edits that have been undone

#     @property
#     def text(self):
#         return self._text

#     def type(self, text):
#         # LOGIC: the "memento" for undo is just the text we're about to append — undoing a type
#         # only ever needs to know HOW MANY characters to chop off the tail.
#         self._text += text
#         self._undo.append(("type", text))
#         # why: a fresh edit invalidates whatever future you'd undone-into — e.g. undo, undo,
#         # then type something new: you can no longer redo back to the old branch.
#         self._redo.clear()

#     def delete(self, n):
#         # LOGIC: clamp n so delete(10) on a 2-char string removes everything, not a negative
#         # slice. e.g. text="hi" (len 2), delete(10) -> n=min(10,2)=2 -> removes both chars.
#         n = min(n, len(self._text))
#         cut = len(self._text) - n
#         removed = self._text[cut:]          # the exact chars we're about to drop — save them
#         self._text = self._text[:cut]
#         self._undo.append(("delete", removed))
#         self._redo.clear()

#     def undo(self):
#         if not self._undo:                  # LOGIC: nothing to undo -> no-op, not an error
#             return
#         kind, payload = self._undo.pop()
#         if kind == "type":
#             # inverse of "we appended `payload`" is "drop the last len(payload) chars".
#             # e.g. undoing type("hello") on text "hello world": keep everything except the
#             # trailing 5 chars that "hello" itself contributed... but note type() always
#             # APPENDS, so those chars are exactly the current tail.
#             self._text = self._text[:len(self._text) - len(payload)]
#         else:  # kind == "delete"
#             # inverse of "we removed `payload` from the tail" is "put it back on the tail".
#             self._text += payload
#         # why: undoing this edit makes it available to REDO — push the same record onto the
#         # other stack so redo() can replay it forward.
#         self._redo.append((kind, payload))

#     def redo(self):
#         if not self._redo:                  # nothing undone yet -> no-op
#             return
#         kind, payload = self._redo.pop()
#         if kind == "type":
#             self._text += payload           # re-apply the append
#         else:  # "delete"
#             self._text = self._text[:len(self._text) - len(payload)]   # re-apply the removal
#         self._undo.append((kind, payload))  # back on the undo stack, so it can be undone again
