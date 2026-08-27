"""
Runnable tests for Tic-Tac-Toe. Write `solution.py` first, then:

    python3 -m unittest test_solution.py -v

Follow-up tests are marked @unittest.skip — remove the decorator when you attempt that follow-up.
"""
import unittest

try:
    from solution import Game, InvalidMove
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    Game = InvalidMove = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )

IN_PROGRESS, WIN, DRAW = "IN_PROGRESS", "WIN", "DRAW"


class TestCore(unittest.TestCase):
    def test_x_starts(self):
        self.assertEqual(Game().current_symbol, "X")

    def test_turns_alternate(self):
        g = Game()
        g.move(0, 0)
        self.assertEqual(g.current_symbol, "O")
        g.move(1, 1)
        self.assertEqual(g.current_symbol, "X")

    def test_x_wins_top_row(self):
        g = Game()
        #   X X X
        #   O O .
        for (r, c) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            self.assertEqual(g.move(r, c), IN_PROGRESS)
        self.assertEqual(g.move(0, 2), WIN)
        self.assertEqual(g.winner, "X")
        self.assertEqual(g.status, WIN)

    def test_win_by_column(self):
        g = Game()
        for (r, c) in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            g.move(r, c)
        self.assertEqual(g.move(2, 0), WIN)  # X column 0
        self.assertEqual(g.winner, "X")

    def test_win_by_main_diagonal(self):
        g = Game()
        for (r, c) in [(0, 0), (0, 1), (1, 1), (0, 2)]:
            g.move(r, c)
        self.assertEqual(g.move(2, 2), WIN)  # X main diagonal
        self.assertEqual(g.winner, "X")

    def test_win_by_anti_diagonal(self):
        g = Game()
        for (r, c) in [(0, 2), (0, 0), (1, 1), (0, 1)]:
            g.move(r, c)
        self.assertEqual(g.move(2, 0), WIN)  # X anti-diagonal
        self.assertEqual(g.winner, "X")

    def test_draw(self):
        g = Game()
        # X O X
        # X O O
        # O X X   -> full, no line
        moves = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 0), (1, 2),
                 (2, 1), (2, 0), (2, 2)]
        result = None
        for m in moves:
            result = g.move(*m)
        self.assertEqual(result, DRAW)
        self.assertIsNone(g.winner)


class TestIllegalMoves(unittest.TestCase):
    def test_occupied_cell(self):
        g = Game()
        g.move(1, 1)
        with self.assertRaises(InvalidMove):
            g.move(1, 1)

    def test_out_of_bounds(self):
        g = Game()
        with self.assertRaises(InvalidMove):
            g.move(3, 0)
        with self.assertRaises(InvalidMove):
            g.move(-1, 0)

    def test_move_after_game_over(self):
        g = Game()
        for (r, c) in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
            g.move(r, c)  # X wins
        with self.assertRaises(InvalidMove):
            g.move(2, 2)


class TestExtensibilityNxN(unittest.TestCase):
    """Follow-up 1: generalize to N x N with N-in-a-row."""

    def test_4x4_row_win(self):
        g = Game(size=4)
        # X fills row 0, O fills row 1 (partial)
        for (r, c) in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]:
            self.assertEqual(g.move(r, c), IN_PROGRESS)
        self.assertEqual(g.move(0, 3), WIN)
        self.assertEqual(g.winner, "X")


if __name__ == "__main__":
    unittest.main(verbosity=2)
