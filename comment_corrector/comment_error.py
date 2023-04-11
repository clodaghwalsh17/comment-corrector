from enum import Enum

class CommentError(Enum):
    OUTDATED_COMMENT = 1
    REMAINING_TASK = 2
    COMMENTED_CODE = 3
    SPELLING_ERROR = 4
    REFACTORED_NAME = 5
    DELETED_NAME = 6