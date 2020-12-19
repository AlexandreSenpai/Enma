from typing import List
from dataclasses import dataclass

from .doujin import DoujinThumbnail

@dataclass
class HomePage:
    doujins: List[DoujinThumbnail]
    total_pages: int = 0

@dataclass
class SearchPage:
    query: str
    sort: str
    total_results: int
    total_pages: int
    doujins: List[DoujinThumbnail]
