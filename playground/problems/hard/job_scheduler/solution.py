"""
JOB SCHEDULER — worked solution with design reasoning (STUDY, THEN WRITE IT YOURSELF).

Solution below the marker is COMMENTED OUT. Read the reasoning, write your own active version
(or strip the leading "# "), then run:  python3 -m unittest test_solution.py -v

────────────────────────────────────────────────────────────────────────────
STEP 1 — NOUNS -> CLASSES, VERBS -> METHODS
  "Jobs declare dependencies on other jobs; a valid run order puts every dependency before its
   dependent; jobs complete one at a time, unlocking whatever was only waiting on them."
    nouns -> Scheduler, Job (id + deps), the dependency graph itself (implicit, not a class)
    verbs -> add_job, get_execution_order, ready, mark_done

STEP 2 — ENTITIES & RELATIONSHIPS
  Scheduler ◆──── jobs (id -> deps)      COMPOSITION: the scheduler IS the graph; jobs are just
                                         entries in its own dict, not separate owned objects.
  "A depends on B" ───▶ association      A job's dep list is a set of REFERENCES (ids) to other
                                         jobs, not ownership — many jobs can point at the same
                                         dependency.
  No inheritance anywhere: a job is (id, deps) — pure data, no behavior of its own. The
  interesting logic (ordering, readiness, cycle detection) belongs to the GRAPH, not to a Job
  class, so a separate Job class would just be data-holding ceremony.

STEP 3 — PATTERN? DAG + topological sort (Kahn's algorithm), not a GoF pattern.
  What varies / what's hard: jobs can be declared in ANY order (deps may reference jobs added
  later), ties must break deterministically, and a cycle must be caught rather than looping
  forever. Kahn's algorithm handles all three at once:
    • in-degree(job) = how many of its deps haven't run yet. A job is runnable once that hits 0.
    • Process runnable jobs with a MIN-HEAP keyed by job_id instead of a plain queue/set — that's
      what makes tie-breaking "ascending job_id" deterministic instead of accidental dict order.
    • "Can we emit every job?" IS the cycle check: each processed job decrements its dependents'
      in-degree; a job stuck in a cycle NEVER reaches in-degree 0 (each of its deps is itself
      waiting on something in the cycle), so it's never emitted. len(order) < len(jobs) at the
      end == some jobs never became runnable == a cycle exists. No separate "visited/visiting"
      DFS coloring needed — Kahn's gets cycle detection for free as a side effect of the count.

STEP 4 — SOLID (+ concurrency note)
  SRP   Scheduler owns graph storage, ordering, and completion state — deliberately not split
        further; a Job class would just be (id, deps) with no behavior, not worth the ceremony.
  OCP   Swapping the tie-break rule (e.g. priority instead of id) only touches what gets pushed
        onto the heap, not the Kahn's-algorithm loop itself.
  CONCURRENCY  mark_done() mutating `completed` while another thread calls ready() is the real
        race (a job could look "ready" from a torn read mid-update). Fix: guard mark_done +
        ready with one lock — this structure doesn't split into fine-grained per-job locks
        cleanly because readiness depends on the WHOLE set of a job's deps at once.
────────────────────────────────────────────────────────────────────────────
"""

# ─── STEP 5 · HOW IT'S USED (declare a diamond, then run it) ──────────────────
#   s = Scheduler()
#   s.add_job("D", ["B", "C"])                 # forward reference: B, C added later — allowed
#   s.add_job("A")
#   s.add_job("B", ["A"])
#   s.add_job("C", ["A"])
#   s.get_execution_order()                    # -> ["A", "B", "C", "D"]  (A first; B before C by
#                                              #    id since both only need A; D last, needs both)
#   s.ready()                                  # -> ["A"]   (only job with zero pending deps)
#   s.mark_done("A")
#   s.ready()                                  # -> ["B", "C"]   (both unlocked by A; D still blocked)
#   s.mark_done("B"); s.mark_done("C")
#   s.ready()                                  # -> ["D"]   (both its deps are now done)
#   # Flow: get_execution_order runs Kahn's ONCE over the whole graph (a static plan); ready()/
#   # mark_done() are the LIVE version of the same idea, driven one completion at a time.
# ─────────────────────────────────────────────────────────────────────────────

# ===== SOLUTION (study, then write your own active version) =====

# import heapq


# class CycleError(Exception):
#     pass


# class Scheduler:
#     def __init__(self):
#         self.jobs = {}            # job_id -> list of dep ids, exactly as declared
#         self.completed = set()    # job_ids marked done

#     def add_job(self, job_id, deps=()):
#         if job_id in self.jobs:
#             raise ValueError(f"duplicate job: {job_id}")
#         self.jobs[job_id] = list(deps)   # copy: caller's list shouldn't be able to mutate us later

#     def _validate_deps(self):
#         # A dep can be declared before the job it points to exists (forward reference is fine at
#         # add_job time) — but by the time we ACT on the graph, every dep must resolve to a real job.
#         for job_id, deps in self.jobs.items():
#             for d in deps:
#                 if d not in self.jobs:
#                     raise KeyError(d)

#     def get_execution_order(self):
#         self._validate_deps()
#         # in_degree[job] = number of deps that haven't "fired" yet in THIS topo pass. Starts as
#         # len(deps); a job becomes runnable the instant this hits 0.
#         in_degree = {job: len(deps) for job, deps in self.jobs.items()}
#         # Reverse edges: for each dep, which jobs are waiting on it? When `dep` gets processed,
#         # walk this list to decrement each waiter's in_degree.
#         dependents = {job: [] for job in self.jobs}
#         for job, deps in self.jobs.items():
#             for d in deps:
#                 dependents[d].append(job)

#         # LOGIC: a min-heap of job_ids, not a plain list/queue — popping always returns the
#         # SMALLEST available id among everything currently runnable, which is exactly the
#         # "ascending job_id" tie-break the contract requires (e.g. roots C, A, B declared in
#         # that order still come out A, B, C).
#         heap = [job for job, deg in in_degree.items() if deg == 0]
#         heapq.heapify(heap)

#         order = []
#         while heap:
#             job = heapq.heappop(heap)
#             order.append(job)
#             for waiter in dependents[job]:
#                 in_degree[waiter] -= 1
#                 if in_degree[waiter] == 0:          # `job` was the LAST thing `waiter` needed
#                     heapq.heappush(heap, waiter)
#         if len(order) != len(self.jobs):
#             # Example: A depends on B, B depends on A. in_degree starts at {A:1, B:1} — the heap
#             # is empty from the start, nothing is ever popped, order stays []. Every job whose
#             # in-degree never reaches 0 is either IN a cycle or depends (transitively) on one;
#             # either way it's missing from `order`, which is the signal we check here.
#             raise CycleError("cycle detected: some jobs are never unblocked")
#         return order

#     def ready(self):
#         self._validate_deps()
#         # A job is ready when it isn't done yet AND every one of its deps IS done — `all()` over
#         # an empty dep list is vacuously True, so a no-deps job is ready immediately.
#         return sorted(
#             job for job in self.jobs
#             if job not in self.completed
#             and all(dep in self.completed for dep in self.jobs[job])
#         )

#     def mark_done(self, job_id):
#         if job_id not in self.jobs:
#             raise KeyError(job_id)
#         self.completed.add(job_id)
