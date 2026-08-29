# Online Quiz Platform 🟡 Medium

**Format:** machine-coding · **Asked as:** a common product-modeling problem · **Time budget:** 60 min
· **Patterns:** Strategy (question types / scoring), clean attempt lifecycle

> A modeling problem with a clear **attempt lifecycle** (in-progress → submitted) and a scoring step.
> The extensible-question-types follow-up is where Strategy naturally appears.

---

## The prompt

> "Design an online quiz platform. A quiz has multiple questions; each has options and one correct
> answer, and is worth some points. A user starts an attempt, answers questions, and submits. On
> submit, compute the score (sum of points for correctly answered questions). Answers can't change
> after submit."

## Clarify before coding

- Single-correct MCQs only? *"Yes for the base; multi-correct / other types are a follow-up."*
- Can a user re-answer a question before submitting? *"Yes — last answer wins."*
- Negative marking? *"No for the base."*
- Multiple concurrent attempts by different users? *"Yes — attempts are independent."*

## Core requirements

1. `create_quiz(quiz_id)`; `add_question(quiz_id, q_id, text, options, correct_index, points=1)`
   (validate `correct_index` is in range).
2. `start_attempt(quiz_id, user_id)` → `attempt_id`.
3. `answer(attempt_id, q_id, option_index)` — record/overwrite; reject unknown question, invalid
   option, or answering after submit (`QuizError`).
4. `submit(attempt_id)` → score = sum of points for correctly answered questions.
5. `score(attempt_id)` returns the score after submission.

## Design hints

Nouns → `Quiz`, `Question`, `Attempt` (answers + status), `QuizPlatform`. Keep an `Attempt` as its
own object with a status so the "no answers after submit" invariant is enforced in one place. Scoring
is a fold over answers; when you add question types (multi-correct, fill-in), make **scoring a
Strategy per question type** rather than a growing `if`.

## Follow-ups (escalations)

1. **Multiple question types** (multi-select, true/false, numeric) — a scoring **Strategy** per type.
2. **Negative marking / partial credit.**
3. **Timed quizzes** (auto-submit on timeout) — inject a clock like the parking-lot/rate-limiter problems.
4. **Randomize question/option order** per attempt; question bank + pick N.
5. **Leaderboards / analytics** across attempts.

## Rubric

- **SDE-1:** correct scoring, attempt lifecycle, validation, independent attempts.
- **SDE-2:** question-type extensibility via Strategy, timed-quiz via injected clock, and a clean
  `Attempt` abstraction that localizes the post-submit invariant.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
