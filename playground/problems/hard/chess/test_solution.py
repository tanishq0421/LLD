"""Runnable tests for Chess (core movement). Write solution.py first."""
import unittest

try:
    from solution import ChessGame, IllegalMove
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    ChessGame = IllegalMove = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestSetup(unittest.TestCase):
    def test_initial_pieces(self):
        g = ChessGame()
        self.assertEqual(g.piece_at("e2"), "wP")
        self.assertEqual(g.piece_at("e1"), "wK")
        self.assertEqual(g.piece_at("d1"), "wQ")
        self.assertEqual(g.piece_at("a1"), "wR")
        self.assertEqual(g.piece_at("b1"), "wN")
        self.assertEqual(g.piece_at("c1"), "wB")
        self.assertEqual(g.piece_at("e7"), "bP")
        self.assertEqual(g.piece_at("e8"), "bK")
        self.assertIsNone(g.piece_at("e4"))

    def test_white_moves_first(self):
        self.assertEqual(ChessGame().turn, "white")


class TestPawn(unittest.TestCase):
    def test_pawn_single_and_double(self):
        g = ChessGame()
        g.move("e2", "e4")             # double from start
        self.assertEqual(g.piece_at("e4"), "wP")
        self.assertIsNone(g.piece_at("e2"))
        self.assertEqual(g.turn, "black")
        g.move("d7", "d6")             # single
        self.assertEqual(g.piece_at("d6"), "bP")

    def test_pawn_illegal_triple(self):
        g = ChessGame()
        with self.assertRaises(IllegalMove):
            g.move("e2", "e5")

    def test_pawn_capture(self):
        g = ChessGame()
        g.move("e2", "e4")
        g.move("d7", "d5")
        g.move("e4", "d5")             # white pawn captures diagonally
        self.assertEqual(g.piece_at("d5"), "wP")
        self.assertIsNone(g.piece_at("e4"))

    def test_pawn_cannot_capture_forward(self):
        g = ChessGame()
        g.move("e2", "e4")
        g.move("e7", "e5")             # pawns face each other
        with self.assertRaises(IllegalMove):
            g.move("e4", "e5")         # blocked, can't capture straight


class TestPieces(unittest.TestCase):
    def test_knight_legal_and_illegal(self):
        g = ChessGame()
        g.move("b1", "c3")             # legal L-shape
        self.assertEqual(g.piece_at("c3"), "wN")
        g.move("b8", "c6")
        with self.assertRaises(IllegalMove):
            g.move("c3", "c5")         # knight can't move straight

    def test_rook_blocked_initially(self):
        g = ChessGame()
        with self.assertRaises(IllegalMove):
            g.move("a1", "a4")         # own pawn on a2 blocks

    def test_bishop_blocked_initially(self):
        g = ChessGame()
        with self.assertRaises(IllegalMove):
            g.move("c1", "e3")         # own pawn on d2 blocks the diagonal

    def test_cannot_move_opponents_piece(self):
        g = ChessGame()                # white to move
        with self.assertRaises(IllegalMove):
            g.move("e7", "e5")         # that's black's pawn

    def test_cannot_capture_own_piece(self):
        g = ChessGame()
        with self.assertRaises(IllegalMove):
            g.move("d1", "e2")         # queen onto own pawn


if __name__ == "__main__":
    unittest.main(verbosity=2)
