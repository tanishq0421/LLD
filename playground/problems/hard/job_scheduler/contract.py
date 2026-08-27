"""
Test contract for the Job Scheduler (DAG + topological sort).

Your `solution.py` must define `Scheduler` and a `CycleError` exception.

    class Scheduler:
        def add_job(self, job_id: str, deps=()) -> None:
            # Register a job with its dependency ids. Raise ValueError on a duplicate job_id.
            # deps may reference jobs added later (declaration order is free).

        def get_execution_order(self) -> list:
            # A valid topological order of ALL jobs (dependencies before dependents).
            # Deterministic: break ties by job_id (ascending).
            # Raise CycleError if the graph has a cycle.
            # Raise KeyError if any dependency references a job that was never added.

        def ready(self) -> list:
            # Jobs whose dependencies are ALL completed and that are not themselves completed yet,
            # sorted by job_id. (Raise KeyError if a dependency references an unknown job.)

        def mark_done(self, job_id: str) -> None:
            # Mark job completed (unlocking dependents). Raise KeyError if the job is unknown.

"A depends on B" means B must run before A.
"""
