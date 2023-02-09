from enum import Enum

class Category(Enum):
    UNTRACKABLE = 1
    DOCUMENTATION = 2
    COPYRIGHT = 3
    TASK = 4
    INLINE = 5
    INLINE_TASK = 6
    MEMBER = 7
    FUNCTION_MEMBER = 8
    INTRO = 9
    ROOT = 10
    OTHER = 11