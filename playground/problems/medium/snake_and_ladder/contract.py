"""
Test contract for Snake & Ladder.

Your `solution.py` must define `Game`:

    class Game:
        def __init__(self, players: list, board_size: int = 100,
                     snakes: dict = None, ladders: dict = None, dice=None):
            # players : list of player-id strings, in turn order.
            # snakes  : {head: tail} with head > tail.
            # ladders : {bottom: top} with bottom < top.
            # dice    : a zero-arg callable returning an int 1..6. Default: random.
            #           Tests inject a scripted callable for determinism.

        @property
        def current_player(self) -> str:
            # id of the player whose turn is next.

        def play_turn(self) -> dict:
            # Roll for current_player and move them. Apply at most one snake/ladder jump.
            # Overshooting board_size => the player stays put (position unchanged).
            # Landing exactly on board_size => that player wins and the game ends.
            # Return a dict:
            #   {"player": pid, "roll": r, "from": old_pos, "to": new_pos, "won": bool}
            # Then advance the turn to the next player (unless the game is over).
            # Raise RuntimeError if called after the game is over.

        def position(self, player_id: str) -> int:
            # Current cell of a player (0 = off-board start).

        @property
        def is_over(self) -> bool: ...

        @property
        def winner(self):
            # winning player id, or None.

Positions start at 0. A player's first roll of r moves them to cell r.
"""
