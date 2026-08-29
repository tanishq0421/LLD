"""
Test contract for the Chat / Messaging System (Mediator).

Your `solution.py` must define `ChatServer` and a `ChatError` exception.

    class ChatServer:
        def create_room(self, room_id: str) -> None:
            # Raise ChatError on a duplicate room_id.

        def join(self, room_id: str, user_id: str) -> None:
            # Add a member. Idempotent. Raise ChatError if the room is unknown.

        def leave(self, room_id: str, user_id: str) -> None:
            # Remove a member. No-op if not a member. Raise ChatError if the room is unknown.

        def send(self, room_id: str, sender: str, message: str) -> list:
            # Deliver `message` to every member EXCEPT the sender; append (sender, message) to
            # history; return the sorted list of recipient ids.
            # Raise ChatError if the room is unknown or `sender` is not a member.

        def members(self, room_id: str) -> list:
            # Sorted list of member ids. Raise ChatError if the room is unknown.

        def history(self, room_id: str) -> list:
            # List of (sender, message) tuples in send order. Raise ChatError if the room is unknown.

Model the room as a Mediator: users interact through the room, not directly with each other.
"""
