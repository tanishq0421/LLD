"""
Test contract for the Hotel Booking System.

Your `solution.py` must define `Hotel`, `Conflict`, and `NoRoomAvailable`.

Dates are integer day numbers; ranges are half-open [check_in, check_out).

    class Hotel:
        def add_room(self, room_id: str, room_type: str) -> None: ...

        def is_available(self, room_id: str, check_in: int, check_out: int) -> bool:
            # True if the room has no booking overlapping [check_in, check_out).

        def find_available(self, room_type: str, check_in: int, check_out: int) -> list:
            # Room ids of that type free for the range, in the order rooms were added.

        def book(self, room_id: str, guest: str, check_in: int, check_out: int) -> str:
            # Book a specific room. Return a unique booking_id.
            # Raise ValueError if check_in >= check_out, KeyError if the room is unknown,
            # Conflict if the dates overlap an existing booking for that room.

        def book_any(self, room_type: str, check_in: int, check_out: int):
            # Book any free room of the type (first free, insertion order).
            # Return (room_id, booking_id). Raise NoRoomAvailable if none is free.

        def cancel(self, booking_id: str) -> None:
            # Free the dates. Raise KeyError if booking_id is unknown.

Overlap of [in1,out1) and [in2,out2) means in1 < out2 and in2 < out1 (checkout day is free).
"""
