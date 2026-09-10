"""
SNAKE & LADDER — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Players roll and advance on a board; a ladder lifts you, a snake drops you; exact landing on
   the final cell wins; overshoot means you don't move."
    nouns -> Board (implicit — snakes+ladders merged into one jump map), Player (just an id +
             position), Dice (injected), Game ; verbs -> play_turn, position

STEP 2 — ENTITIES & RELATIONSHIPS
  Game ◆──── jump map (snakes+ladders)   COMPOSITION: built once at construction from the dicts
                                          handed in; Game owns it, nothing else references it.
  Game o──── Dice                        DEPENDENCY INJECTION: the die is a zero-arg callable
                                          PASSED IN (aggregation), not `random.randint` called
                                          inline — that's what makes a game REPRODUCIBLE in tests
                                          (inject a scripted callable that yields fixed rolls).
  Game ───▶ players (list of ids)        ASSOCIATION: Game just tracks each id's int position in
                                          a dict; no separate Player class needed — a player IS
                                          its id + an int, no behaviour of its own (no class needed
                                          for data with zero behaviour — resist the urge to make one).
  NO inheritance for snakes vs ladders — both are just "landing on cell X sends you to cell Y";
  they collapse into ONE dict (cell -> destination) with no need for two classes.

STEP 3 — PATTERN? (what varies?)
  Two swappable seams, both handled via DI/Strategy rather than a GoF class hierarchy:
    • the DICE — injected callable so tests can script rolls (`scripted([3,6,6,5])`). This is a
      textbook Strategy (the "how to roll" algorithm is pluggable) done the lightweight Python
      way: a function, not a class with an interface.
    • the WIN/JUMP rule — "exact landing wins, overshoot stays put, at most one jump" is one fixed
      policy here; a follow-up (bounce-back on overshoot, chained jumps) would be a second
      Strategy object Game delegates to, instead of an `if` inside play_turn.
  No Factory/State machinery needed for the base — board entities are DATA (a dict), not a class
  hierarchy; adding machinery here would be over-engineering a problem that's really "one dict
  lookup and one comparison." Name the seam, don't build it unless asked.

STEP 4 — SOLID (+ CONCURRENCY)
  SRP   Game owns turn order + movement rules; the jump map is pure data, not logic.
  OCP   a new movement/win rule = swap what play_turn delegates to, not an edit to every branch.
  CONCURRENCY  two threads calling play_turn() concurrently on the same Game would interleave
        read (`current_player`) and write (`positions[...] = ...`) — lock the whole turn (a board
        game is inherently one-turn-at-a-time, so a single lock around play_turn is CORRECT here,
        unlike the parking-lot/rate-limiter cases where a single lock would over-serialize).
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (a ladder lift, then a winning roll) ──────────────
#   rolls = scripted([3, 6, 2])                    # injected dice: deterministic sequence
#   g = Game(["p1"], board_size=20, ladders={3: 11}, dice=rolls)
#   g.current_player                                # "p1"
#   g.play_turn()                                    # roll=3: 0->3, ladder 3->11 -> {"to":11,...}
#   g.position("p1")                                  # 11
#   g.play_turn()                                    # roll=6: 11->17 (no jump on 17 here)
#   g.play_turn()                                    # roll=2: 17->19 (< 20, no win)
#   g.is_over                                         # False
#   # Flow: play_turn -> dice() -> raw = pos+roll -> overshoot? stay : apply jump map -> win check
#   #       -> record result -> advance current_player (only if game continues).
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import random


# class Game:
#     def __init__(self, players, board_size=100, snakes=None, ladders=None, dice=None):
#         self.players = list(players)
#         self.board_size = board_size
#         # LOGIC: snakes (head->tail) and ladders (bottom->top) are both "land here, jump there" —
#         # merge them into ONE lookup so play_turn does a single dict.get instead of two checks.
#         self.jumps = {}
#         self.jumps.update(ladders or {})
#         self.jumps.update(snakes or {})
#         # DI: a fake dice in tests scripts exact rolls; production falls back to a real d6.
#         self.dice = dice or (lambda: random.randint(1, 6))
#         self.positions = {p: 0 for p in players}   # everyone starts off-board at cell 0
#         self._turn_idx = 0
#         self._is_over = False
#         self._winner = None

#     @property
#     def current_player(self):
#         return self.players[self._turn_idx]

#     @property
#     def is_over(self):
#         return self._is_over

#     @property
#     def winner(self):
#         return self._winner

#     def position(self, player_id):
#         return self.positions[player_id]

#     def play_turn(self):
#         if self._is_over:
#             raise RuntimeError("game is already over")
#         pid = self.current_player
#         old_pos = self.positions[pid]
#         roll = self.dice()
#         landed = old_pos + roll
#         won = False
#         if landed > self.board_size:
#             # LOGIC: overshoot -> stay put. Example: at 18 on a 20-board, rolling 5 -> 23 > 20,
#             # so the player doesn't move at all this turn (not even partway).
#             new_pos = old_pos
#         elif landed == self.board_size:
#             # LOGIC: exact landing on the final cell wins immediately — no jump map applied to
#             # the winning cell itself, the game simply ends there.
#             new_pos = landed
#             won = True
#         else:
#             # LOGIC: apply AT MOST ONE jump. jumps.get(landed, landed) means "if this cell has a
#             # snake head or ladder bottom, teleport; otherwise stay on the plain cell you landed on."
#             new_pos = self.jumps.get(landed, landed)
#         self.positions[pid] = new_pos
#         result = {"player": pid, "roll": roll, "from": old_pos, "to": new_pos, "won": won}
#         if won:
#             self._is_over = True
#             self._winner = pid
#             # game is over — do NOT advance the turn (no "next player" once someone's won).
#         else:
#             # LOGIC: round-robin turn order — wrap back to player 0 after the last player.
#             self._turn_idx = (self._turn_idx + 1) % len(self.players)
#         return result
