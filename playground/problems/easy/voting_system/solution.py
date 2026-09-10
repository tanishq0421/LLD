"""
VOTING SYSTEM — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Create polls with fixed options; each voter votes once; tally results; close a poll to new
   votes."
    nouns -> VotingSystem (registry), Poll (question + options + tally + open/closed)
    verbs -> create_poll, vote, results, close_poll
  "Voter" needs no class: a voter is just an id string used to enforce "one vote each" — a set of
  ids already captures everything we need to know about them.

STEP 2 — ENTITIES & RELATIONSHIPS
  VotingSystem ◆──── Poll×N       COMPOSITION: polls are created BY create_poll and live only
                                  inside the system's registry; nothing external holds one.
  Poll ◆──── counts, voted_ids    COMPOSITION: a poll owns its own tally dict and the set of
                                  voter ids who've already voted — private bookkeeping, not
                                  shared with other polls.
  NO inheritance: one Poll shape covers every poll; "closed" is a boolean FLAG (data), not a
  reason to fork into OpenPoll/ClosedPoll subclasses.

STEP 3 — PATTERN? (what varies?)
  Nothing here varies in a way that wants a GoF pattern — there's one poll shape, one voting
  rule set, one tally format. This is a NO-PATTERN problem: the actual skill being tested is
  enforcing invariants cleanly (unique poll id, valid option, one vote per voter, respect
  closed state) with guard clauses, not picking a pattern. Reaching for Strategy/State here
  would be over-engineering a shape with nothing left to swap.

STEP 4 — SOLID (+ concurrency note)
  SRP   VotingSystem = poll registry + id-uniqueness. Poll = its own tally + one-vote-per-voter
        enforcement. Neither knows about the other's internals beyond the registry lookup.
  OCP   A richer PollStatus (DRAFT/OPEN/CLOSED) would slot in later without touching vote()'s
        validation ORDER — today a plain `closed` boolean is enough (YAGNI).
  CONCURRENCY  Two votes from the SAME voter_id racing could both pass the "have they voted?"
        check before either records it -> a double vote. Fix: lock the check-and-record step per
        poll (not globally across all polls, which would serialize unrelated elections).
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (object flow / a run-through) ─────────────────────
#   v = VotingSystem()
#   v.create_poll("p1", "Best language?", ["python", "java", "go"])   # tally starts {opt:0,...}
#   v.vote("p1", "u1", "python")     # u1 -> python; voted_ids={u1}, counts["python"]=1
#   v.vote("p1", "u1", "java")       # u1 already voted -> raises VotingError, counts unchanged
#   v.vote("p1", "u2", "go")         # different voter -> counts["go"]=1
#   v.results("p1")                  # {"python": 1, "java": 0, "go": 1}  (every option, incl. 0s)
#   v.close_poll("p1")               # poll.closed = True
#   v.vote("p1", "u3", "python")     # closed -> raises VotingError
#   # Flow: create_poll seeds a Poll in the registry -> vote()/results()/close_poll() look it up
#   # by id and delegate to that Poll's own state.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# class VotingError(Exception):
#     pass


# class _Poll:
#     # LOGIC: private (leading underscore) — an implementation detail of VotingSystem, not part
#     # of the public contract, so callers only ever talk to VotingSystem.
#     def __init__(self, question, options):
#         self.question = question
#         self.options = options
#         # LOGIC: seed every option at 0 up front so results() always reports ALL options,
#         # including ones nobody voted for yet (dict comprehension over the options list).
#         self.counts = {option: 0 for option in options}
#         self.voted_ids = set()     # voter_ids who've already cast a vote in THIS poll
#         self.closed = False

#     def vote(self, voter_id, option):
#         if self.closed:
#             raise VotingError("poll is closed")
#         if option not in self.counts:
#             raise VotingError(f"invalid option {option!r}")
#         if voter_id in self.voted_ids:
#             raise VotingError(f"voter {voter_id!r} has already voted")
#         self.voted_ids.add(voter_id)
#         self.counts[option] += 1


# class VotingSystem:
#     def __init__(self):
#         self._polls = {}     # poll_id -> _Poll

#     def create_poll(self, poll_id, question, options):
#         if poll_id in self._polls:
#             raise VotingError(f"poll {poll_id!r} already exists")
#         if not options:
#             raise VotingError("a poll needs at least one option")
#         self._polls[poll_id] = _Poll(question, options)

#     def _get(self, poll_id):
#         # LOGIC: shared lookup for vote/results/close_poll so the "unknown poll" error message
#         # and exception type stay consistent across all three call sites (DRY).
#         poll = self._polls.get(poll_id)
#         if poll is None:
#             raise VotingError(f"unknown poll {poll_id!r}")
#         return poll

#     def vote(self, poll_id, voter_id, option):
#         self._get(poll_id).vote(voter_id, option)

#     def results(self, poll_id):
#         # LOGIC: return a COPY of the tally dict, not the live one — so a caller mutating the
#         # returned dict can't silently corrupt the poll's real counts.
#         return dict(self._get(poll_id).counts)

#     def close_poll(self, poll_id):
#         self._get(poll_id).closed = True
