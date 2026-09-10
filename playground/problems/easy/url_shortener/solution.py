"""
URL SHORTENER — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Turn a long URL into a short code and back; codes can be custom or auto-generated, and must
   never collide."
    nouns -> URLShortener (the registry/service), a code<->URL mapping
    verbs -> shorten, expand, delete

STEP 2 — ENTITIES & RELATIONSHIPS
  URLShortener ◆──── {code: url}   COMPOSITION: the shortener owns its mapping outright — it's
                                   created and destroyed with the shortener, nothing external
                                   holds a reference to it.
  No separate "ShortURL" class: a (code, url) pair carries no behaviour of its own, so a plain
  dict entry is enough — inventing a class here would be needless ceremony.

STEP 3 — PATTERN? (what varies?)
  WHAT varies: HOW an auto-generated code is produced. Here: an ever-incrementing counter,
  rendered in BASE62 (0-9, a-z, A-Z = 62 symbols) so small counters make short, URL-safe codes —
  counter 1 -> "1", counter 61 -> "Z", counter 62 -> "10" (like decimal rolling 9 -> 10, but base
  62). This is arithmetic, not a GoF pattern, but it's the standard interview answer to "how do
  you guarantee uniqueness without a hash-collision check?".
  The SEAM worth naming out loud: the "next id" counter is, in a real (distributed) system, the
  one thing that MUST be centrally coordinated — a canonical example of where a Singleton (or a
  single shared counter service, e.g. a DB sequence) is the honest answer, because two counters
  in two processes would hand out duplicate ids. Here it's just instance state on URLShortener;
  name the seam, don't build a global for a single-process toy version (YAGNI).

STEP 4 — SOLID (+ concurrency note)
  SRP   URLShortener does storage + code generation only — no HTTP routing, no analytics.
  OCP   Swapping the generation strategy (base62 counter -> random hash -> Snowflake id) means
        changing ONE method (_next_code); shorten/expand/delete never change.
  CONCURRENCY  Two shorten() calls racing on the SAME counter could read-then-increment the same
        value and hand out the same code twice. Fix: make the read-increment step atomic (a lock,
        or an atomic/DB counter) — exactly the failure mode a single shared id generator (the
        Singleton seam above) exists to prevent.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (object flow / a run-through) ─────────────────────
#   s = URLShortener()
#   c1 = s.shorten("https://example.com/a/b/c")   # no alias -> auto code via base62 counter -> "1"
#   s.expand(c1)                                  # "https://example.com/a/b/c"
#   c2 = s.shorten("https://example.com/a/b/c")   # SAME url, again no alias -> counter bumps -> "2"
#   c1 == c2                                      # False (two codes for the same URL, by design)
#   s.shorten("https://promo.com", alias="promo") # custom code "promo" used as-is
#   s.shorten("https://x.com", alias="promo")     # "promo" already taken -> raises AliasTaken
#   s.delete(c1)                                  # mapping removed
#   s.expand(c1)                                  # raises KeyError (gone)
#   # Flow: shorten() picks/validates a code -> stores {code: url} -> expand()/delete() look it up.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# _ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"  # 62 URL-safe symbols


# def _to_base62(n):
#     # LOGIC: same trick as converting to any base — repeatedly take n mod 62 as the next digit
#     # (least-significant first), then integer-divide n by 62, until n hits 0; reverse at the end.
#     # Example: n=63 -> 63 % 62 = 1 -> digit _ALPHABET[1] = "1", n //= 62 -> n=1
#     #                -> 1 % 62 = 1  -> digit "1",                n //= 62 -> n=0 -> stop.
#     #          digits collected as ["1", "1"], reversed -> "11" (just like decimal rolls
#     #          9 -> 10 when you run out of single digits, base62 rolls 61(="Z") -> "10").
#     if n == 0:
#         return _ALPHABET[0]
#     digits = []
#     while n:
#         n, remainder = divmod(n, 62)
#         digits.append(_ALPHABET[remainder])
#     return "".join(reversed(digits))


# class AliasTaken(Exception):
#     pass


# class URLShortener:
#     def __init__(self):
#         self._urls = {}      # short_code -> long_url
#         self._counter = 0    # LOGIC: bumped once per AUTO-generated code, never reused/reset

#     def shorten(self, long_url, alias=None):
#         if alias is not None:
#             # CUSTOM alias: caller picks the code; it must not already be in use by anyone.
#             if alias in self._urls:
#                 raise AliasTaken(f"alias {alias!r} is already in use")
#             code = alias
#         else:
#             code = self._next_code()
#         self._urls[code] = long_url
#         return code

#     def _next_code(self):
#         # LOGIC: keep bumping the counter and re-encoding until we land on a code nobody's
#         # holding (guards against an auto code accidentally matching a custom alias someone
#         # already claimed, e.g. alias="1"). In practice this loop runs once almost always.
#         while True:
#             self._counter += 1
#             code = _to_base62(self._counter)
#             if code not in self._urls:
#                 return code

#     def expand(self, short_code):
#         # LOGIC: dict[key] raises KeyError automatically on a missing code — exactly what the
#         # contract asks for, so no explicit check-then-raise needed here.
#         return self._urls[short_code]

#     def delete(self, short_code):
#         # LOGIC: `del dict[key]` also raises KeyError on a missing key, matching the contract.
#         del self._urls[short_code]
