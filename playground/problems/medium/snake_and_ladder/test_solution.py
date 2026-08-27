"""Runnable tests for Snake & Ladder. Write solution.py first."""
import unittest

try:
    from solution import Game
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Game = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


def scripted(rolls):
    """Return a dice callable that yields the given rolls in order."""
    it = iter(rolls)
    return lambda: next(it)


class TestMovement(unittest.TestCase):
    def test_ladder_lifts_player(self):
        g = Game(["p1"], board_size=20, ladders={3: 11}, dice=scripted([3]))
        info = g.play_turn()
        self.assertEqual(info["from"], 0)
        self.assertEqual(info["to"], 11)   # 0 -> 3 -> ladder -> 11
        self.assertEqual(g.position("p1"), 11)

    def test_snake_drops_player(self):
        g = Game(["p1"], board_size=20, snakes={17: 4}, dice=scripted([6, 6, 5]))
        g.play_turn()  # 0 -> 6
        g.play_turn()  # 6 -> 12
        info = g.play_turn()  # 12 -> 17 -> snake -> 4
        self.assertEqual(info["to"], 4)
        self.assertEqual(g.position("p1"), 4)

    def test_overshoot_stays_put(self):
        g = Game(["p1"], board_size=20, dice=scripted([6, 6, 6, 5]))
        for _ in range(3):
            g.play_turn()  # 0->6->12->18
        self.assertEqual(g.position("p1"), 18)
        info = g.play_turn()  # 18 + 5 = 23 > 20 -> stay
        self.assertEqual(info["to"], 18)
        self.assertFalse(info["won"])

    def test_exact_landing_wins(self):
        g = Game(["p1"], board_size=20, dice=scripted([6, 6, 6, 2]))
        for _ in range(3):
            g.play_turn()  # -> 18
        info = g.play_turn()  # 18 + 2 = 20 -> win
        self.assertTrue(info["won"])
        self.assertTrue(g.is_over)
        self.assertEqual(g.winner, "p1")


class TestTurnsAndGuards(unittest.TestCase):
    def test_turn_rotation(self):
        g = Game(["p1", "p2"], board_size=50, dice=scripted([3, 4, 5]))
        self.assertEqual(g.current_player, "p1")
        g.play_turn()
        self.assertEqual(g.current_player, "p2")
        g.play_turn()
        self.assertEqual(g.current_player, "p1")

    def test_no_play_after_game_over(self):
        g = Game(["p1"], board_size=6, dice=scripted([6, 6]))
        g.play_turn()  # 0 -> 6 win
        self.assertTrue(g.is_over)
        with self.assertRaises(RuntimeError):
            g.play_turn()

    def test_no_jump_when_cell_is_plain(self):
        g = Game(["p1"], board_size=20, snakes={17: 4}, ladders={3: 11},
                 dice=scripted([5]))
        info = g.play_turn()  # lands on 5, no jump
        self.assertEqual(info["to"], 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
