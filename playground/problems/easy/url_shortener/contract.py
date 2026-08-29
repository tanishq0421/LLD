"""
Test contract for the URL Shortener.

Your `solution.py` must define `URLShortener` and an `AliasTaken` exception.

    class URLShortener:
        def __init__(self): ...

        def shorten(self, long_url: str, alias: str = None) -> str:
            # Return a unique short code (string). If `alias` is given, use it as the code;
            # raise AliasTaken if that alias is already in use.
            # Auto-generated codes must be unique (e.g. counter + base62).

        def expand(self, short_code: str) -> str:
            # Return the original URL for a code. Raise KeyError if unknown.

        def delete(self, short_code: str) -> None:
            # Remove a mapping. Raise KeyError if unknown.

Two different auto-generated codes must never collide. How you encode them is your design.
"""
