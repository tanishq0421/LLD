# Job / Task Scheduler with Dependencies 🔴 Hard (DAG + topological sort)

**Format:** machine-coding · **Asked by:** Google, Amazon, Microsoft, Meta, Uber (build systems,
workflow engines, CI) · **Time budget:** 60–75 min · **Patterns:** graph modeling (DAG), topological
sort; Command/Strategy for job execution

> The "can you model a dependency graph" problem — the brain behind Make, Airflow, Gradle, CI
> pipelines. The core skills: build a DAG, produce a valid **topological order**, and **detect
> cycles**. Then layer on "which jobs can run now" as dependencies complete.

---

## The prompt

> "Design a job scheduler where jobs can depend on other jobs. A job can only run after all its
> dependencies have completed. Produce a valid execution order for all jobs, detect cycles (an
> impossible schedule), and at any point report which jobs are ready to run given what has completed."

## Clarify before coding

- Can dependencies be declared before the jobs they reference exist? *"Yes — allow declaring in any order; validate that all referenced jobs exist when scheduling."*
- Multiple valid orders — any valid one, or a specific tie-break? *"Any valid topological order; make it deterministic (e.g. sort ties by id)."*
- What on a cycle? *"Raise an error — it's an impossible schedule."*
- Parallel execution? *"Report ready jobs; actual parallel running is a follow-up."*

## Core requirements

1. `add_job(job_id, deps=())` — register a job and its dependency ids (error on duplicate id).
2. `get_execution_order()` → a valid topological order of all jobs; raise `CycleError` on a cycle;
   raise `KeyError` if a dependency references an unknown job.
3. `ready()` → jobs whose dependencies are all completed and which aren't completed yet (deterministic order).
4. `mark_done(job_id)` → mark a job completed, unlocking its dependents.

## Design hints

Model jobs as nodes and "A depends on B" as an edge B→A. **Kahn's algorithm** (repeatedly take
nodes with in-degree 0) gives a topological order *and* detects cycles (if you can't emit all nodes,
there's a cycle). For `ready()`, a job is runnable when every dependency is in the completed set.
Sort tie-breaks by id for determinism. Nouns → `Job`, `Scheduler`, an execution `Strategy`.

## Follow-ups (escalations)

1. **Parallel execution:** run all ready jobs concurrently; as each finishes, recompute ready set (a worker pool).
2. **Failure handling:** a failed job blocks its dependents; retries with backoff; `skip`/`abort` policy.
3. **Priorities / deadlines** among independent ready jobs; resource limits (max N concurrent).
4. **Dynamic graphs:** adding jobs/edges at runtime; incremental re-scheduling.
5. **Cron/time triggers** and idempotent re-runs.

## Rubric

- **SDE-1:** correct topological order, cycle detection, ready-set, mark_done unlocking dependents.
- **SDE-2:** clean DAG abstraction, deterministic ordering, and a concrete plan for parallel
  execution + failure handling + resource limits.

## Your task

Write `solution.py` exposing [`contract.py`](contract.py), then `python3 -m unittest test_solution.py -v`.
