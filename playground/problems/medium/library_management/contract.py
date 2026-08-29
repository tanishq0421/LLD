"""
Test contract for the Library Management System.

Your `solution.py` must define `Library` and a `LibraryError` exception.

    class Library:
        def __init__(self, max_borrow: int = 3):
            # max_borrow: how many books one member may hold at once.

        def add_book(self, isbn: str, title: str, copies: int = 1) -> None:
            # Register a book, or add more copies if the ISBN already exists.

        def add_member(self, member_id: str) -> None:
            # Register a member. Raise LibraryError on a duplicate.

        def borrow(self, member_id: str, isbn: str) -> None:
            # Borrow one available copy. Raise LibraryError if:
            #   - member or book is unknown,
            #   - no copies are available,
            #   - the member is already at the borrow limit,
            #   - the member already holds this title.

        def return_book(self, member_id: str, isbn: str) -> None:
            # Return a held copy. Raise LibraryError if the member is not holding this title.

        def available(self, isbn: str) -> int:
            # Number of available copies. Raise LibraryError if the book is unknown.

        def borrowed_by(self, member_id: str) -> list:
            # Sorted list of ISBNs the member currently holds. Raise LibraryError if member unknown.
"""
