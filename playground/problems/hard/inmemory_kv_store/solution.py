"""
IN-MEMORY KV STORE WITH NESTED TRANSACTIONS — worked solution with design reasoning
(STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "A store holds keys; transactions can nest; begin opens a layer, commit merges it down,
   rollback discards it; get/count always see the EFFECTIVE (innermost) value."
    nouns -> KVStore, base store, transaction layer (overlay)
    verbs -> get, set, delete, count, begin, commit, rollback
  There's no separate "Transaction" object with its own identity — a transaction IS a dict
  of pending writes. Giving it a class would just be a dict with extra ceremony (YAGNI).

STEP 2 — ENTITIES & RELATIONSHIPS
  KVStore ◆──── base dict        COMPOSITION: the permanent, committed key -> value state.
  KVStore ◆──── stack of overlays  COMPOSITION: each open begin() pushes one overlay dict;
                                  the stack's length == nesting depth. Overlays die with the
                                  store (or with commit/rollback).
  An overlay maps key -> value OR key -> DELETED (a sentinel meaning "this txn deletes it,
  even if an outer layer/base still has it"). Without the sentinel we could NOT distinguish
  "this txn didn't touch the key" (fall through to parent) from "this txn deleted the key"
  (stop here, key is gone) — a plain dict.pop() inside the overlay would incorrectly re-expose
  the parent's value.
  NO inheritance anywhere: layers differ only in POSITION on the stack, not behavior.

STEP 3 — PATTERN? (what varies?)
  This is an OVERLAY STACK (a lightweight Memento/Snapshot idea): each begin() snapshots
  "everything from here down is frozen; new writes go on top." commit == squash top layer
  into the one below; rollback == pop and discard. Modeling nested transactions as a STACK
  OF DIFFS (rather than deep-copying the whole store on every begin) is what makes commit/
  rollback O(size of that transaction's writes) instead of O(size of whole store).

STEP 4 — SOLID
  SRP  KVStore owns exactly one job: layered key resolution. get/count don't know HOW many
       layers exist; they just walk the stack top-down.
  OCP  Want savepoints-with-names, or read-only transactions? Extend the overlay's shape
       (e.g. add metadata to each layer) without touching get()'s walk-down logic.
  Concurrency note (not required here, but worth saying out loud): this design is
  single-writer-in-mind — nested transactions model ONE caller's pending edits, not
  concurrent callers. Multiple threads sharing one KVStore would need a lock around
  begin/set/delete/commit/rollback, since the stack itself is mutated.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (nested transactions, commit inner, rollback outer) ───
#   kv = KVStore()
#   kv.set("a", 1)                      # no txn open -> straight into base: base={"a":1}
#   kv.begin()                          # push outer overlay: stack=[{}]
#   kv.set("a", 2)                      # writes into stack[-1]: stack=[{"a":2}]
#   kv.begin()                          # push inner overlay: stack=[{"a":2}, {}]
#   kv.set("a", 3)                      # stack=[{"a":2}, {"a":3}]
#   kv.get("a")                         # 3  (innermost layer wins)
#   kv.rollback()                       # discard inner -> stack=[{"a":2}]
#   kv.get("a")                         # 2  (outer layer, untouched by the discarded inner)
#   kv.commit()                         # merge outer into base -> base={"a":2}; stack=[]
#   kv.get("a")                         # 2
#   # Flow: writes always land on stack[-1] (or base if stack empty); get() walks the stack
#   # top-down and falls through to base; commit squashes stack[-1] into stack[-2]/base;
#   # rollback just pops stack[-1] and throws it away.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# DELETED = object()   # LOGIC: a unique sentinel — distinct from any real value (even None) —
#                       # meaning "this layer deletes the key". A plain dict can't represent
#                       # "explicitly absent" any other way without this marker.


# class NoTransaction(Exception):
#     pass


# class KVStore:
#     def __init__(self):
#         self.base = {}     # committed state: key -> value (never holds DELETED)
#         self.stack = []     # open transactions, outermost first; each is key -> value|DELETED

#     def get(self, key):
#         # LOGIC: walk from innermost (stack[-1]) down to outermost (stack[0]), then base.
#         # The FIRST layer that mentions this key wins — that's the "effective" value.
#         # e.g. stack=[{"a":2}, {"a":3}] -> reversed gives {"a":3} first -> return 3.
#         for layer in reversed(self.stack):
#             if key in layer:
#                 v = layer[key]
#                 return None if v is DELETED else v
#         return self.base.get(key)   # no open layer mentions it -> fall through to base

#     def set(self, key, value):
#         # LOGIC: writes always target the innermost open layer (the "current" transaction).
#         # If none is open, self.stack is empty, so stack[-1] would IndexError -> use base.
#         target = self.stack[-1] if self.stack else self.base
#         target[key] = value

#     def delete(self, key):
#         # LOGIC: inside a txn we can't just pop the key from the overlay — that would leave
#         # the txn silent on "a", and get() would fall through and re-expose an outer/base
#         # value that's supposed to be hidden. We must record "deleted HERE" explicitly.
#         if self.stack:
#             self.stack[-1][key] = DELETED
#         else:
#             self.base.pop(key, None)   # no txn: deleting a missing key is a no-op

#     def count(self, value):
#         # LOGIC: "value" is the number of KEYS whose CURRENT effective value equals `value`.
#         # A key might live only in an overlay (never in base) or only in base — so first
#         # collect every key that's mentioned ANYWHERE (base ∪ every open layer), then ask
#         # get() (which already knows how to resolve layering) what each one currently is.
#         keys = set(self.base)
#         for layer in self.stack:
#             keys.update(layer)
#         return sum(1 for k in keys if self.get(k) == value)

#     def begin(self):
#         self.stack.append({})   # LOGIC: a fresh, empty overlay — nothing written here yet.

#     def commit(self):
#         if not self.stack:
#             raise NoTransaction("no open transaction to commit")
#         layer = self.stack.pop()               # innermost layer, about to be squashed down
#         target = self.stack[-1] if self.stack else self.base
#         # LOGIC: replay every entry of the committed layer onto its parent. If the parent
#         # is `base` (a real dict, no sentinel allowed in it), a DELETED entry means "actually
#         # remove this key from base". If the parent is another overlay, just copy the raw
#         # value (DELETED included) — overlays are allowed to carry the sentinel themselves.
#         if target is self.base:
#             for k, v in layer.items():
#                 if v is DELETED:
#                     target.pop(k, None)
#                 else:
#                     target[k] = v
#         else:
#             target.update(layer)

#     def rollback(self):
#         if not self.stack:
#             raise NoTransaction("no open transaction to roll back")
#         self.stack.pop()   # LOGIC: just drop the innermost layer — its writes never happened.
