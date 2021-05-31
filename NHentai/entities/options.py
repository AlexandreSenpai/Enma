from enum import Enum, unique
from typing import List, Optional

@unique
class Sort(Enum):
    RECENT: str = 'recent'
    TODAY: str = 'popular-today'
    WEEK: str = 'popular-week'
    MONTH: str = 'popular-month'
    YEAR: str = 'popular-year'
    ALL_TIME: str = 'popular'
