"""
Test contract for BookMyShow (movie ticket booking).

Your `solution.py` must define `BookingService` and a `SeatUnavailable` exception.

    class BookingService:
        def add_show(self, show_id: str, seat_ids: list) -> None:
            # Register a show with its seats (all initially available).

        def available_seats(self, show_id: str) -> list:
            # Sorted list of seat ids that are not currently booked.
            # Raise KeyError for an unknown show.

        def book(self, show_id: str, seat_ids: list, user_id: str) -> str:
            # Atomically book ALL seat_ids for user_id. Return a unique booking_id.
            # If ANY requested seat is already booked, book NONE and raise SeatUnavailable.
            # Raise KeyError for an unknown show or unknown seat id.
            # MUST be safe under concurrent calls: at most one booking per seat, ever.

        def cancel(self, booking_id: str) -> None:
            # Free all seats in the booking. Raise KeyError for an unknown booking_id.

        def get_booking(self, booking_id: str) -> dict:
            # {"show_id": ..., "user_id": ..., "seats": [...]}. KeyError if unknown.

Everything else — seat state representation, locking strategy, id generation — is your design.
"""
