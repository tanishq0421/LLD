"""
LOGGING FRAMEWORK — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "A logger holds a minimum severity; a message at or above it gets formatted and emitted."
    nouns -> Logger, level (DEBUG/INFO/WARNING/ERROR), message, record
    verbs -> log (generic), debug/info/warning/error (convenience wrappers around log)
  Level names are a closed, ORDERED value set -> a small name->rank map (an Enum with IntEnum
  values would also work; a plain dict is enough for a base problem and keeps ordering explicit).

STEP 2 — ENTITIES & RELATIONSHIPS
  Logger ───▶ LEVELS map     ASSOCIATION: the logger reads a fixed rank table; it doesn't own or
                              mutate it, so it's shared/reusable data, not composed state.
  NO inheritance for DebugLogger/InfoLogger/etc. — the four convenience methods differ only in
  WHICH level constant they pass to log(), not in behaviour. One class, one min_level field.

STEP 3 — PATTERN? (what varies?)
  Nothing varies enough here to justify a pattern for the base problem — forcing a Strategy for
  "how to filter" or a Chain of Responsibility for "which handler processes this" would be
  over-engineering four lines of comparison logic. WORTH NAMING for a follow-up: if this grew
  multiple SINKS (console, file, network) each formatting/writing differently, that's the classic
  home for the OBSERVER pattern (Logger notifies a list of Handler/Appender objects) or a Strategy
  per output format — but the base problem only has one sink (the returned list), so skip it.

STEP 4 — SOLID
  SRP  Logger's only job is "should this pass the level filter, and if so, format it." It does not
       know about files, sockets, or timestamps.
  OCP  Adding a new level or changing thresholds is a data change (LEVELS map / min_level), not a
       rewrite of log(). Adding a new SINK later means adding a Handler object the logger calls
       into, not adding an if/elif inside log().
  DIP  A real logger should depend on an abstract "where do records go" (a sink/handler interface)
       injected in, rather than hard-coding print()/file-writes — the base problem sidesteps I/O
       entirely by RETURNING the formatted records, which is what makes it testable without mocks.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (object flow / a run-through) ─────────────────────
#   log = Logger(min_level="WARNING")     # only WARNING and ERROR will be emitted
#   log.debug("cache miss")               # DEBUG(10) < WARNING(30) -> filtered -> []
#   log.info("request handled")           # INFO(20)  < WARNING(30) -> filtered -> []
#   log.warning("disk at 90%")            # WARNING(30) >= WARNING(30) -> ["WARNING: disk at 90%"]
#   log.error("disk full")                # ERROR(40) >= WARNING(30) -> ["ERROR: disk full"]
#   log.log("ERROR", "via generic")       # same path as .error(), just called directly
#   # Flow: caller -> debug/info/warning/error (fix the level string) -> log (rank-compare against
#   #        min_level, format "LEVEL: message" if it passes) -> caller gets back a list of 0 or 1
#   #        formatted records (a list, not a single string, leaves room for a future multi-sink
#   #        emit that could return more than one formatted line per call).
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# # LOGIC: numeric rank per level name — higher number = more severe. Comparing severities becomes
# # a plain integer comparison instead of string comparison (which would sort alphabetically, wrong).
# LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}


# class Logger:
#     def __init__(self, min_level="INFO"):
#         self.min_level = min_level

#     def log(self, level, message):
#         # LOGIC: emit only if this message's rank is >= the logger's configured minimum rank.
#         # e.g. WARNING(30) >= INFO(20) -> True -> emitted; DEBUG(10) >= INFO(20) -> False -> dropped.
#         if LEVELS[level] >= LEVELS[self.min_level]:
#             return [f"{level}: {message}"]
#         return []               # filtered out -> no records produced

#     def debug(self, message):
#         return self.log("DEBUG", message)

#     def info(self, message):
#         return self.log("INFO", message)

#     def warning(self, message):
#         return self.log("WARNING", message)

#     def error(self, message):
#         return self.log("ERROR", message)
