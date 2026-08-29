"""Runnable tests for the Online Quiz Platform. Write solution.py first."""
import unittest

try:
    from solution import QuizPlatform, QuizError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    QuizPlatform = QuizError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


def platform():
    p = QuizPlatform()
    p.create_quiz("q")
    p.add_question("q", "q1", "2+2?", ["3", "4", "5"], correct_index=1, points=1)
    p.add_question("q", "q2", "capital of France?", ["Paris", "Rome"], correct_index=0, points=2)
    p.add_question("q", "q3", "sky color?", ["green", "blue"], correct_index=1, points=1)
    return p


class TestScoring(unittest.TestCase):
    def test_all_correct(self):
        p = platform()
        a = p.start_attempt("q", "u1")
        p.answer(a, "q1", 1)
        p.answer(a, "q2", 0)
        p.answer(a, "q3", 1)
        self.assertEqual(p.submit(a), 4)   # 1 + 2 + 1

    def test_partial(self):
        p = platform()
        a = p.start_attempt("q", "u1")
        p.answer(a, "q1", 1)   # correct (1)
        p.answer(a, "q2", 1)   # wrong (0)
        # q3 unanswered (0)
        self.assertEqual(p.submit(a), 1)

    def test_points_weighting(self):
        p = platform()
        a = p.start_attempt("q", "u1")
        p.answer(a, "q2", 0)   # the 2-point question
        self.assertEqual(p.submit(a), 2)

    def test_last_answer_wins(self):
        p = platform()
        a = p.start_attempt("q", "u1")
        p.answer(a, "q1", 0)   # wrong
        p.answer(a, "q1", 1)   # overwrite with correct
        self.assertEqual(p.submit(a), 1)

    def test_score_after_submit(self):
        p = platform()
        a = p.start_attempt("q", "u1")
        p.answer(a, "q1", 1)
        p.submit(a)
        self.assertEqual(p.score(a), 1)


class TestGuards(unittest.TestCase):
    def test_answer_after_submit(self):
        p = platform()
        a = p.start_attempt("q", "u1")
        p.submit(a)
        with self.assertRaises(QuizError):
            p.answer(a, "q1", 1)

    def test_invalid_option(self):
        p = platform()
        a = p.start_attempt("q", "u1")
        with self.assertRaises(QuizError):
            p.answer(a, "q1", 9)

    def test_unknown_question(self):
        p = platform()
        a = p.start_attempt("q", "u1")
        with self.assertRaises(QuizError):
            p.answer(a, "qX", 0)

    def test_unknown_quiz_attempt(self):
        p = platform()
        with self.assertRaises(QuizError):
            p.start_attempt("ghost", "u1")

    def test_bad_correct_index(self):
        p = QuizPlatform()
        p.create_quiz("z")
        with self.assertRaises(QuizError):
            p.add_question("z", "q1", "x", ["a", "b"], correct_index=5)

    def test_independent_attempts(self):
        p = platform()
        a1 = p.start_attempt("q", "u1")
        a2 = p.start_attempt("q", "u2")
        p.answer(a1, "q2", 0)   # u1 correct on 2-pointer
        self.assertEqual(p.submit(a1), 2)
        self.assertEqual(p.submit(a2), 0)   # u2 answered nothing


if __name__ == "__main__":
    unittest.main(verbosity=2)
