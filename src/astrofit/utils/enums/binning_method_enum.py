from enum import Enum, auto


class BinningMethodEnum(Enum):
    FIRST_TO_FIRST_DIFF = auto()
    LAST_TO_FIRST_DIFF = auto()
