# URL Shortener 🟢 Easy (LLD flavor)

**Format:** machine-coding / OOD · **Asked by:** Google, Microsoft, Amazon, Meta, Twitter, LinkedIn
(as an HLD↔LLD crossover) · **Time budget:** 40 min · **Patterns:** encoding, Singleton (id
generator), Strategy (encoding scheme)

> Usually framed as system design, but the **LLD core** is tight and testable: generate a unique
> short code, store the mapping, expand it back, handle custom aliases and expiry. (A pastebin /
> text-sharing service is the *same* problem — a code that maps to stored content instead of a URL.)

---

## The prompt

> "Design a URL shortening service. `shorten(long_url)` returns a short code; `expand(short_code)`
> returns the original URL. Support optional **custom aliases** and reject collisions. Codes should be
> short and unique."

## Clarify before coding

- Random codes or a counter + base62 encoding? *"Counter → base62 is simplest and collision-free."*
- Custom aliases allowed? *"Yes; reject if the alias is already taken."*
- Same long URL twice → same code or new one? *"New mapping each time is fine (dedup is a follow-up)."*
- Expiry / TTL? *"Optional — treat as a follow-up."*

## Core requirements

1. `shorten(long_url, alias=None)` → a unique short code. With `alias`, use it; raise `AliasTaken`
   if that alias already exists.
2. `expand(short_code)` → the original URL; `KeyError` if unknown.
3. `delete(short_code)` removes a mapping.
4. Auto-generated codes are unique (counter + base62 keeps them collision-free).

## Design hints

Keep an incrementing counter and encode it in **base62** `[0-9a-zA-Z]` for the auto code — unique by
construction, no collision checks needed. Keep a `code → url` map for `expand`. Custom aliases go into
the same namespace (check-and-reject). The id generator is a natural **Singleton**; the encoding is a
swappable **Strategy** (base62 vs hash vs random).

## Follow-ups (escalations)

1. **Expiry/TTL** and lazy purge of expired codes (like the LRU-TTL follow-up).
2. **Deduplicate** identical URLs to one code (reverse index url → code).
3. **Analytics:** click counts per code (leads toward the HLD version).
4. **Distributed id generation** at scale (counter ranges / Snowflake) — the HLD boundary.
5. **Pastebin variant:** map the code to stored *content* + a syntax/expiry instead of a URL.

## Rubric

- **SDE-1:** correct shorten/expand round-trip, unique codes, custom aliases + collision rejection.
- **SDE-2:** base62 vs hashing trade-off, dedup + TTL design, and where distributed id generation
  takes over at scale.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
