from enum import Enum

class Status(Enum):
    UNCHECKED = 1
    CHECKED = 2
    SPELLING_ERRORS = 3
    REMAINING_TASKS = 4
    OUTDATED_COMMENTS = 5