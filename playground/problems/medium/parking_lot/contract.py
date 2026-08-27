"""
Test contract for the Parking Lot.

Your `solution.py` must define `ParkingLot`, `ParkingFull`, and `InvalidTicket`.

Spot sizes and vehicle types are plain strings:
    SPOT TYPES   : "SMALL", "MEDIUM", "LARGE"
    VEHICLE TYPES: "MOTORCYCLE", "CAR", "TRUCK"

Fit rule (a vehicle can use its own size or larger):
    MOTORCYCLE -> SMALL, MEDIUM, LARGE
    CAR        -> MEDIUM, LARGE
    TRUCK      -> LARGE
Allocation: assign the SMALLEST compatible free spot (best-fit).

    class ParkingLot:
        def __init__(self, clock=None, hourly_rates=None):
            # clock: a zero-arg callable returning the current time in SECONDS.
            #        Defaults to time.time. Tests inject a controllable clock.
            # hourly_rates: optional dict {vehicle_type: rate}. Default below.
            #        Fee = ceil(duration_hours) * rate, minimum 1 hour.

        def add_spot(self, spot_id: str, spot_type: str) -> None: ...

        def park(self, vehicle_id: str, vehicle_type: str) -> str:
            # Assign the smallest compatible free spot; record entry time via clock().
            # Return a ticket id (string). Raise ParkingFull if nothing compatible is free.

        def unpark(self, ticket_id: str) -> int:
            # Free the spot; return the fee computed from (clock() - entry_time).
            # Raise InvalidTicket for an unknown or already-closed ticket.

        def available_count(self, spot_type: str = None) -> int:
            # Free spots total, or for a given size if spot_type is provided.

Default hourly rates the tests assume:
    {"MOTORCYCLE": 10, "CAR": 20, "TRUCK": 30}
Fee formula the tests assume: hours = max(1, ceil(duration_seconds / 3600)); fee = hours * rate.
"""

DEFAULT_HOURLY_RATES = {"MOTORCYCLE": 10, "CAR": 20, "TRUCK": 30}
