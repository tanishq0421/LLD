"""
Test contract for the Ride-Hailing service.

Your `solution.py` must define `RideService`, `NoDriverAvailable`, and `InvalidTrip`.

Locations are integer (x, y); distance is Manhattan: |x1-x2| + |y1-y2|.
Trip status strings: "ASSIGNED", "ONGOING", "COMPLETED", "CANCELLED".

    class RideService:
        def __init__(self, pricing=None):
            # pricing: callable(distance:int) -> number. Default: 50 + 10*distance.

        def register_driver(self, driver_id: str, x: int, y: int) -> None:
            # Register (or re-register) a driver, available at (x, y).

        def request_ride(self, rider_id: str, x: int, y: int) -> str:
            # Assign the NEAREST available driver (Manhattan; tie-break by driver_id).
            # Mark that driver busy, create a trip in "ASSIGNED", return a unique trip_id.
            # Raise NoDriverAvailable if no driver is free.
            # MUST be safe under concurrency: never assign one driver to two active trips.

        def start_trip(self, trip_id: str) -> None:
            # "ASSIGNED" -> "ONGOING". Raise InvalidTrip otherwise. KeyError if unknown trip.

        def end_trip(self, trip_id: str, drop_x: int, drop_y: int):
            # "ONGOING" -> "COMPLETED". Return the fare = pricing(distance(pickup, drop)).
            # Free the driver (available at the drop location). Raise InvalidTrip otherwise.

        def cancel_trip(self, trip_id: str) -> None:
            # From "ASSIGNED" or "ONGOING" -> "CANCELLED"; free the driver.
            # Raise InvalidTrip if already COMPLETED/CANCELLED.

        def trip_status(self, trip_id: str) -> str: ...     # KeyError if unknown

        def get_driver(self, trip_id: str) -> str:
            # driver_id assigned to the trip. KeyError if unknown.
"""
