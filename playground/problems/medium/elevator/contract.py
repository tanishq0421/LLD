"""
Test contract for the Elevator (single car, LOOK algorithm).

Your `solution.py` must define `Elevator`:

    class Elevator:
        def __init__(self, current_floor: int = 0, min_floor: int = 0, max_floor: int = 10):
            ...

        def request_floor(self, floor: int) -> None:
            # Add a destination floor. Raise ValueError if outside [min_floor, max_floor].
            # Requesting the current floor is allowed (it will be serviced on the next step()).

        def step(self) -> None:
            # Advance the simulation by one time unit using the LOOK algorithm:
            #   - If standing on a target floor, service it (remove it) — this counts as the
            #     step's action (the car does not also move this step).
            #   - Otherwise, if there are targets, ensure a sensible direction (from IDLE, head
            #     toward the nearest target; keep the current direction while targets remain ahead,
            #     else reverse), then move exactly one floor in that direction.
            #   - If no targets remain, set direction to "IDLE".

        @property
        def current_floor(self) -> int: ...

        @property
        def direction(self) -> str:
            # "UP", "DOWN", or "IDLE".

        @property
        def targets(self) -> set:
            # The set of pending target floors (a copy is fine).

The exact tie-breaking between two equidistant targets is your choice; the tests avoid ties.
"""
