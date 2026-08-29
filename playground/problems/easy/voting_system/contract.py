"""
Test contract for the Polling / Voting System.

Your `solution.py` must define `VotingSystem` and a `VotingError` exception.

    class VotingSystem:
        def create_poll(self, poll_id: str, question: str, options: list) -> None:
            # Create a poll with a non-empty list of option labels. Raise VotingError on a duplicate
            # poll_id or empty options.

        def vote(self, poll_id: str, voter_id: str, option: str) -> None:
            # Record voter_id's vote for `option`. Raise VotingError if:
            #   - the poll is unknown,
            #   - `option` is not one of the poll's options,
            #   - voter_id has already voted in this poll,
            #   - the poll is closed.

        def results(self, poll_id: str) -> dict:
            # {option: count} for EVERY option (including zeros). Raise VotingError if unknown poll.

        def close_poll(self, poll_id: str) -> None:
            # Close the poll; further votes must be rejected. Raise VotingError if unknown poll.
"""
