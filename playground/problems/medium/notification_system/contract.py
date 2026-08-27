"""
Test contract for the Notification System (Observer + Strategy/Adapter).

Your `solution.py` must define `NotificationService` and a `NotificationError` exception.

    class NotificationService:
        def register_channel(self, name: str, sender) -> None:
            # Register a delivery channel. `sender` is a callable sender(recipient, message) -> None
            # (the uniform interface each channel/provider adapts to).

        def subscribe(self, user: str, channel: str) -> None:
            # Add `channel` to the user's preferences. Idempotent.
            # Raise NotificationError if the channel is not registered.

        def unsubscribe(self, user: str, channel: str) -> None:
            # Remove `channel` from the user's preferences. No-op if not subscribed.

        def notify(self, user: str, message: str) -> list:
            # Deliver `message` via every channel the user is subscribed to, calling
            # sender(user, message) for each. Return the list of channel names that delivered,
            # in the order the channels were registered on the service (deterministic).
            # A user with no subscriptions -> [] (no error).

Everything else — how you store channels/preferences, adapter classes — is your design.
"""
