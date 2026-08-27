# How to Practice — Simulating a Real LLD Round

This repo is built so you can run a **realistic mock LLD round** by yourself: read the prompt
cold, design, code in a blank file, then run hidden tests to see if you passed — followed by
follow-up escalations, exactly like the real thing.

---

## The 3 phases of a real round (mirror them)

| Phase | Time (of a 90-min round) | What you do |
|---|---|---|
| **1. Pre-coding** | ~10–15 min | Read prompt twice. Ask/clarify. Underline **nouns → classes**, **verbs → methods**. Sketch entities + a rough class diagram (boxes/arrows — formal UML NOT required). State your public API. |
| **2. Coding** | ~55–65 min | Implement. Narrate trade-offs out loud (even alone — practice it). Keep it simple; add complexity only when forced. |
| **3. Post-coding** | ~15–20 min | Run the tests. Walk through your design. Take the **follow-up escalations** and explain (or code) how your design absorbs them. |

> **Reminder from the research:** you're **never handed a UML diagram** — you derive it.
> A formal UML diagram is *not* a required deliverable in either format; a rough sketch as a
> *thinking step* is. Don't fixate on notation.

---

## The per-problem workflow

Each `problems/<tier>/<name>/` folder has:

```
README.md          ← the prompt, clarifying Qs, requirements, follow-ups, rubric, time budget
contract.py        ← the small public interface the tests call (your ONLY constraint)
test_solution.py   ← runnable tests: core + follow-up scenarios
```

**Recommended loop:**

1. **Open only `README.md`.** Read the prompt. **Do not read the tests yet** — that's cheating
   your own clarifying-question practice. Spend 10 min designing on paper.
2. Create your own `solution.py` in that folder. Implement the classes/behavior. Your solution
   must expose the entry points listed in `contract.py` (that's the "hand off to the test
   harness" — everything *behind* those entry points is your design to make).
3. Run the tests (see below). Iterate until green.
4. Now open `README.md`'s **Follow-ups** section and take them one at a time — re-design and
   extend. Some tests are marked as follow-ups and are **skipped by default**; enable them as
   you tackle each escalation.
5. Read the **Rubric** last. Grade yourself honestly against the SDE-1 and SDE-2 bars.

### About `contract.py` (important, honest note)
Real classic-OOP LLD rounds usually give you a **blank editor**, not a required interface — you
design the public API yourself. This repo fixes a *minimal* public contract per problem for one
reason only: **so automated tests can call your code.** Treat it as "the interviewer said: expose
these operations." Everything below the surface — classes, patterns, data structures — is yours.
If you'd rather practice fully blank, ignore `contract.py`, design your own API, and adapt the
test file's import/calls to match.

---

## Running the tests

From inside a problem folder, name your file `solution.py` and run (zero dependencies):

```bash
python3 -m unittest test_solution.py -v
```

Or run every problem's tests at once with the helper script (from the repo root):

```bash
./run_tests.sh
```

Each problem shows as passing, failing, or "awaiting solution.py". Filter to one problem with
`./run_tests.sh splitwise`.

> Don't use `python3 -m unittest discover` from the repo root — each problem imports its own local
> `solution` module, so tests must run from inside the problem folder (which `run_tests.sh` does).

`pytest` also works per-folder if you prefer it (`pip install pytest` then `pytest -v`), but nothing
here requires it — `unittest` is in the standard library.

### Enabling follow-up tests
Follow-up/stretch tests use `@unittest.skip(...)`. When you attempt that escalation, delete the
skip decorator (or run with `python3 -m unittest test_solution.py -v` after removing it) to
turn the test on.

---

## Self-scoring rubric (applies to every problem)

Grade each 0–2 (0 = missing, 1 = partial, 2 = solid):

| Dimension | SDE-1 bar | SDE-2 bar |
|---|---|---|
| **Correctness** | Happy path + basic edge cases pass | All edge cases + concurrency correctness |
| **Requirement clarification** | Asked the obvious questions | Drove scope & surfaced ambiguity unprompted |
| **Class design / SOLID** | Reasonable classes, SRP mostly held | Clean SRP/OCP, composition over inheritance |
| **Extensibility** | Can add a feature with some edits | New feature = new class, no core edits |
| **Right patterns (not over-engineered)** | Used a fitting pattern when natural | Justified *why*, and where NOT to use one |
| **Concurrency** (SDE-2 critical) | Aware of the race | Fine-grained locking / correct thread-safety |
| **Communication** | Explained the code | Narrated trade-offs, compared alternatives |

**Time check:** did you produce *working* code inside the time budget? Running out of time with a
beautiful un-compiled design is the #1 machine-coding failure.

---

## Common failure modes to self-check (from the research)

- ❌ Over-engineering — factories/builders where a plain class works (KISS). **Named red flag.**
- ❌ Coding before designing → drowning in edge cases. Or over-designing → no time to code.
- ❌ Skipping requirement clarification → wrong class responsibilities.
- ❌ Solving silently → interviewer can't assess your reasoning.
- ❌ Premature optimization — DB/caching/threading before it's asked.
- ❌ Deep inheritance where composition fits.
- ❌ Ignoring edge cases (invalid input, concurrency, failures).
