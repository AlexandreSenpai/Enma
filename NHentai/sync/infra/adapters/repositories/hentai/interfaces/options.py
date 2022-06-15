from enum import Enum, unique
from typing import List, Optional

@unique
class Sort(Enum):
    TODAY: str = 'popular-today'
    WEEK: str = 'popular-week'
    ALL_TIME: str = 'popular'
    RECENT = None