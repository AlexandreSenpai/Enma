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
    total_pages: int
    doujins: List[DoujinThumbnail]

@dataclass
class GroupListPage:
    page: int
    total_pages: int
    groups: List[str]

@dataclass
class CharacterListPage:
    page: int
    total_pages: int
    characters: List[str]

@dataclass
class ArtistListPage:
    page: int
    total_pages: int
    artists: List[str]

@dataclass
class TagListPage:
    page: int
    total_pages: int
    tags: List[str]

