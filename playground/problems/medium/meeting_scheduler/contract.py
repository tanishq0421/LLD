"""
Test contract for the Meeting Room Scheduler.

Your `solution.py` must define `MeetingScheduler`, `Conflict`, and `NoRoomAvailable`.

Intervals are half-open [start, end) with integer times.

    class MeetingScheduler:
        def add_room(self, room_id: str) -> None: ...

        def book(self, room_id: str, start: int, end: int) -> str:
            # Book [start, end) in room_id. Return a unique booking_id.
            # Raise ValueError if start >= end. Raise Conflict if it overlaps an existing booking
            # in that room. Raise KeyError if the room is unknown.

        def is_available(self, room_id: str, start: int, end: int) -> bool:
            # True if [start, end) does not overlap any booking in room_id.

        def available_rooms(self, start: int, end: int) -> list:
            # Room ids free for [start, end), in the order rooms were added.

        def book_any(self, start: int, end: int):
            # Book [start, end) in any free room (first free, in insertion order).
            # Return (room_id, booking_id). Raise NoRoomAvailable if none is free.

        def cancel(self, booking_id: str) -> None:
            # Free the slot. Raise KeyError if booking_id is unknown.

Overlap of [s1,e1) and [s2,e2) means s1 < e2 and s2 < e1 (back-to-back does NOT conflict).
"""
