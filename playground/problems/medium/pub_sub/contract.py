"""
Test contract for the in-memory Pub/Sub broker.

Your `solution.py` must define `Broker` and a `PubSubError` exception.

    class Broker:
        def create_topic(self, topic: str) -> None:
            # Create a topic. Raise PubSubError if it already exists.

        def publish(self, topic: str, message) -> int:
            # Append `message` to the topic's log. Return its 0-based offset.
            # Raise PubSubError if the topic does not exist.

        def subscribe(self, topic: str, subscriber: str) -> None:
            # Register a subscriber on the topic, starting at offset 0 (sees the full backlog).
            # Raise PubSubError if the topic does not exist.

        def poll(self, topic: str, subscriber: str) -> list:
            # Return the messages this subscriber has not yet consumed (in publish order) and
            # advance its offset to the end. A second poll with no new messages returns [].
            # Raise PubSubError if the topic/subscriber is unknown.

Each subscriber tracks its own offset; two subscribers to one topic each receive every message.
Publish/poll should be safe to call concurrently (the concurrency test covers this).
"""
