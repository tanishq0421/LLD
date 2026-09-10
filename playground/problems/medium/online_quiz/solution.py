"""
ONLINE QUIZ PLATFORM — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Quizzes hold MCQ questions; a user starts an attempt, answers questions, submits, gets a score."
    nouns -> QuizPlatform, Quiz, Question, Attempt ; verbs -> create_quiz, add_question,
    start_attempt, answer, submit, score

STEP 2 — ENTITIES & RELATIONSHIPS
  QuizPlatform ◆──── Quiz              COMPOSITION: quizzes only exist inside the platform.
  Quiz ◆──── Question                  COMPOSITION: a question has no meaning outside its quiz
                                        (q_ids are only unique WITHIN a quiz).
  QuizPlatform ◆──── Attempt           COMPOSITION: an attempt is platform-managed state.
  Attempt ───▶ Quiz                    ASSOCIATION: an attempt REFERENCES the quiz it's for (by
                                        quiz_id) to look up questions/points at submit time; it
                                        doesn't own the quiz.
  NO inheritance for "single-correct MCQ" — it's the only question shape asked for; a
  hierarchy of question TYPES (MCQ / multi-select / free-text) would be speculative here.

STEP 3 — PATTERN? (what varies?)
  STRATEGY (named, not built): scoring is "sum points for each question where the chosen option
  == correct_index." That rule is exactly the kind of thing that varies across quiz platforms —
  partial credit, negative marking for wrong answers, multiple-correct questions, time-decay
  bonuses. Today there's exactly ONE rule, so it's a plain method (`_score_attempt`), not a
  ScoringStrategy interface — building the interface for a single implementation is speculative
  generality. Name the seam out loud: "swap `_score_attempt` for an injected strategy the moment
  a second scoring rule shows up."
  ATTEMPT LIFECYCLE (the actual crux): an attempt moves through in-progress -> submitted, a tiny
  one-way state machine. `answer()` is only legal pre-submit; `score()` is only legal
  post-submit. That's enforced with a `submitted` flag, same lightweight approach as the ATM's
  state string — no separate State classes for two states and one transition.

STEP 4 — SOLID (+ concurrency note)
  SRP   Quiz/Question data, attempt bookkeeping, and the scoring rule are three distinct bits of
        code (add_question validates question shape; answer validates an attempt's input;
        _score_attempt is pure scoring math) — each can change independently.
  OCP   a new scoring rule = a new strategy plugged into submit(), not edits to answer()/state
        tracking. A new question type = a new "add_*_question" + matching scorer, same shape.
  CONCURRENCY  two answer() calls for the SAME attempt+question racing is a last-write-wins
        dict assignment — fine here since the contract explicitly wants "last answer wins"
        (test_last_answer_wins); the only real race to guard in a multi-user deployment is two
        submit() calls on the same attempt double-finalizing — guard with a lock or an
        atomic compare-and-set on `submitted`.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (build a quiz, take it, score it) ─────────────────
#   p = QuizPlatform()
#   p.create_quiz("q")
#   p.add_question("q", "q1", "2+2?", ["3", "4", "5"], correct_index=1, points=1)
#   p.add_question("q", "q2", "capital of France?", ["Paris", "Rome"], correct_index=0, points=2)
#   a = p.start_attempt("q", "u1")             # fresh attempt_id, e.g. "A1"
#   p.answer(a, "q1", 1)                       # correct so far
#   p.answer(a, "q1", 0)                       # OVERWRITES q1's answer -> now wrong
#   p.answer(a, "q2", 0)                       # correct
#   p.submit(a)                                # 0 (q1 wrong) + 2 (q2 right) = 2 ; locks the attempt
#   p.score(a)                                 # 2  (re-readable after submit)
#   p.answer(a, "q1", 1)                       # QuizError: already submitted
#   # Flow: answer() just records the LATEST choice per question; all the actual scoring math
#   # happens once, lazily, inside submit() by comparing each recorded choice to correct_index.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import itertools


# class QuizError(Exception):
#     pass


# class QuizPlatform:
#     def __init__(self):
#         self.quizzes = {}     # quiz_id -> { q_id -> {"options": [...], "correct": i, "points": p} }
#         self.attempts = {}    # attempt_id -> {"quiz_id", "answers": {q_id: option_index}, "submitted", "score"}
#         self._seq = itertools.count(1)

#     def create_quiz(self, quiz_id):
#         if quiz_id in self.quizzes:
#             raise QuizError(f"quiz {quiz_id!r} already exists")
#         self.quizzes[quiz_id] = {}          # starts with no questions

#     def add_question(self, quiz_id, q_id, text, options, correct_index, points=1):
#         if quiz_id not in self.quizzes:
#             raise QuizError(f"unknown quiz {quiz_id!r}")
#         quiz = self.quizzes[quiz_id]
#         if q_id in quiz:
#             raise QuizError(f"duplicate question id {q_id!r}")
#         # LOGIC: correct_index must point at a REAL option (0..len(options)-1), otherwise no
#         # answer could ever be marked correct — catch that authoring bug at add-time, not scoring
#         # time. e.g. options=["a","b"] (len 2) -> valid indices are 0,1 -> range(2) = {0,1}.
#         if not (0 <= correct_index < len(options)):
#             raise QuizError("correct_index out of range for options")
#         quiz[q_id] = {"text": text, "options": options, "correct": correct_index, "points": points}

#     def start_attempt(self, quiz_id, user_id):
#         if quiz_id not in self.quizzes:
#             raise QuizError(f"unknown quiz {quiz_id!r}")
#         attempt_id = f"A{next(self._seq)}"
#         self.attempts[attempt_id] = {
#             "quiz_id": quiz_id,
#             "user_id": user_id,
#             "answers": {},        # q_id -> chosen option_index ; empty = unanswered
#             "submitted": False,
#             "score": None,
#         }
#         return attempt_id

#     def answer(self, attempt_id, q_id, option_index):
#         attempt = self.attempts.get(attempt_id)
#         if attempt is None:
#             raise QuizError(f"unknown attempt {attempt_id!r}")
#         if attempt["submitted"]:
#             raise QuizError("attempt already submitted")
#         quiz = self.quizzes[attempt["quiz_id"]]
#         if q_id not in quiz:
#             raise QuizError(f"question {q_id!r} not in this quiz")
#         if not (0 <= option_index < len(quiz[q_id]["options"])):
#             raise QuizError("option_index out of range")
#         # LOGIC: plain dict assignment == "last write wins" — answering q1 twice just overwrites
#         # the stored choice, which is exactly what test_last_answer_wins expects.
#         attempt["answers"][q_id] = option_index

#     def submit(self, attempt_id):
#         attempt = self.attempts.get(attempt_id)
#         if attempt is None:
#             raise QuizError(f"unknown attempt {attempt_id!r}")
#         if attempt["submitted"]:
#             raise QuizError("attempt already submitted")
#         quiz = self.quizzes[attempt["quiz_id"]]
#         # SCORING "STRATEGY" (today's only rule): sum points for every question whose recorded
#         # answer matches its correct_index. Unanswered questions simply aren't in `answers`, so
#         # they contribute 0 automatically — no special-casing needed.
#         total = sum(
#             q["points"] for q_id, q in quiz.items()
#             if attempt["answers"].get(q_id) == q["correct"]
#         )
#         attempt["submitted"] = True
#         attempt["score"] = total
#         return total

#     def score(self, attempt_id):
#         attempt = self.attempts.get(attempt_id)
#         if attempt is None or not attempt["submitted"]:
#             raise QuizError("attempt not yet submitted")
#         return attempt["score"]
