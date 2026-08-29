"""
Test contract for the Online Quiz Platform.

Your `solution.py` must define `QuizPlatform` and a `QuizError` exception.

    class QuizPlatform:
        def create_quiz(self, quiz_id: str) -> None:
            # Raise QuizError on a duplicate quiz_id.

        def add_question(self, quiz_id: str, q_id: str, text: str, options: list,
                         correct_index: int, points: int = 1) -> None:
            # Add a single-correct MCQ. Raise QuizError if quiz unknown, duplicate q_id, or
            # correct_index out of range for options.

        def start_attempt(self, quiz_id: str, user_id: str) -> str:
            # Return a unique attempt_id. Raise QuizError if the quiz is unknown.

        def answer(self, attempt_id: str, q_id: str, option_index: int) -> None:
            # Record (or overwrite) the answer. Raise QuizError if: attempt unknown, already
            # submitted, q_id not in the quiz, or option_index out of range.

        def submit(self, attempt_id: str) -> int:
            # Finalize the attempt and return the score = sum of `points` for correctly answered
            # questions. Raise QuizError if already submitted or attempt unknown.

        def score(self, attempt_id: str) -> int:
            # The score of a submitted attempt. Raise QuizError if not yet submitted / unknown.
"""
