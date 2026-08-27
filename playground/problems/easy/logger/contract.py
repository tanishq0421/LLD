"""
Test contract for the Logging Framework.

Your `solution.py` must define `Logger`:

    class Logger:
        def __init__(self, min_level: str = "INFO"):
            # min_level is one of "DEBUG", "INFO", "WARNING", "ERROR".

        def log(self, level: str, message: str) -> list:
            # If `level` >= min_level, emit and RETURN the list of formatted records produced,
            # e.g. ["ERROR: disk full"].  If filtered out, return [].
            # (Returning the emitted records — instead of only printing — is what makes the
            #  framework testable. A real logger would also write them to a sink.)

        def debug(self, message: str) -> list:    ...   # == log("DEBUG", message)
        def info(self, message: str) -> list:     ...   # == log("INFO", message)
        def warning(self, message: str) -> list:  ...   # == log("WARNING", message)
        def error(self, message: str) -> list:    ...   # == log("ERROR", message)

Formatting for the base problem is "LEVEL: message" (e.g. "INFO: started"). Level ordering:
DEBUG(10) < INFO(20) < WARNING(30) < ERROR(40).
"""

LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
