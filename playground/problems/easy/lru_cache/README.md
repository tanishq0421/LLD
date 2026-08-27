# LRU Cache 🟢 Easy (data-structure design)

**Format:** machine-coding / DSA-flavored OOD · **Asked by:** Google, Amazon, Microsoft, Meta,
Adobe, Netflix · **Time budget:** 30–40 min · **Patterns:** none required (it's about picking the
right data structures)

---

## The prompt

> "Design an LRU (Least Recently Used) cache with a fixed capacity. `get(key)` returns the value
> and marks the key as most-recently used. `put(key, value)` inserts or updates, and when the
> cache exceeds capacity it evicts the least-recently-used entry. Both operations should be O(1)."

This is as much a data-structures problem as a design one — the interviewer is checking whether
you reach for a **hash map + doubly linked list** (O(1) move-to-front + O(1) eviction) rather than
scanning a list.

## Clarify before coding

- Is `get` on a missing key an error or a sentinel (`-1`/`None`)? *"Raise `KeyError` for this exercise."*
- Does `get` count as a use (update recency)? *"Yes."*
- Does updating an existing key via `put` refresh recency? *"Yes."*
- Capacity ≥ 1 guaranteed? *"Yes."*

## Core requirements

1. `LRUCache(capacity)` — fixed positive capacity.
2. `get(key)` — return value and mark most-recently-used; raise `KeyError` if absent/evicted.
3. `put(key, value)` — insert/update, mark most-recently-used, evict LRU when over capacity.
4. `len(cache)` — current number of entries.
5. Both `get` and `put` are **O(1)**.

## Design hints

`dict` for O(1) lookup + a **doubly linked list** for O(1) recency reordering and tail eviction.
(Python note: `collections.OrderedDict` gives you `move_to_end` + `popitem(last=False)` for free —
fine to use, but be ready to explain the linked-list version, since interviewers often ask you to
implement it without the library.)

## Follow-ups (escalations)

1. **TTL:** entries expire after a time-to-live; expired entries are misses and get purged.
2. **LFU** (Least *Frequently* Used) instead of LRU — how does your structure change?
   *(This is a genuinely harder redesign — freq buckets.)*
3. **Thread-safety:** many threads calling `get`/`put`. Where's the race, and what do you lock?
   (A single lock is correct but coarse; discuss finer options.)
4. **Max memory (bytes) instead of entry count**, with variable-size values.

## Rubric

- **SDE-1:** correct eviction, `get` refreshes recency, O(1) with dict + linked list (or OrderedDict).
- **SDE-2:** can implement the doubly linked list by hand, explains the TTL/LFU redesign, and gives
  a correct thread-safety story.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
