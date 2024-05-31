from enum import Enum, auto


class BinningMethod(Enum):
    FIRST_TO_FIRST_DIFF = auto()
    LAST_TO_FIRST_DIFF = auto()
